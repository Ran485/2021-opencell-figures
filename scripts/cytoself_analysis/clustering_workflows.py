
import collections
import anndata as ad
import numpy as np
import scipy as sp
import pandas as pd
import scanpy as sc
import scanpy.external as sce
import sknetwork

import sklearn
import sklearn.cluster
import sklearn.manifold
import sklearn.decomposition
from sklearn.metrics import (
    adjusted_rand_score, adjusted_mutual_info_score
)

from matplotlib import pyplot as plt
from matplotlib import rcParams

# these packages are not available on ESS
try:
    import leidenalg
    from pySankey import sankey
except ImportError:
    pass

from .model_results import SCATTERPLOT_COLORS
from . import ground_truth_labels
from ..external import complex_comparison


class ClusteringWorkflow:

    def __init__(self, adata=None, filepath=None):
        if adata is not None:
            self.adata = adata        
        elif filepath is not None:
            self.adata = ad.read_h5ad(filepath)
        self.original_adata = adata.copy()


    def preprocess(
        self,
        do_log1p=False,
        do_scaling=True,
        n_top_genes=None,
        n_pcs=200,
    ):
        '''
        Our canonical scanpy-based preprocessing workflow for either VQ2 vectors or histograms
        '''
        # start from the original adata object
        self.adata = self.original_adata.copy()
        adata = self.adata
        
        # log-transform (for histogram-based adata only)
        if do_log1p:
            sc.pp.log1p(adata)

        # select highly variable features
        if n_top_genes is not None:
            sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes)

        # scale to zero mean and unit variance
        if do_scaling:
            sc.pp.scale(adata, max_value=10)

        # PCA
        if n_pcs is not None:
            sc.pp.pca(adata, n_comps=n_pcs, use_highly_variable=(n_top_genes is not None))


    def calculate_neighbors(self, n_pcs=200, n_neighbors=10, metric='euclidean'):
        '''
        Computing the weighted adjacency matrix (what umap alls the fuzzy_simplicial_set)
        '''
        sc.pp.neighbors(
            self.adata, 
            method='umap', 
            metric=metric,
            n_neighbors=n_neighbors,
            n_pcs=n_pcs,
            knn=True, 
        )


    def calculate_neighbors_sam(self):
        '''
        The workflow for computing the weighted adjacency matrix using the SAM embedding algorithm
        '''
        ...


    def run_leiden(self, resolution, from_sam=False, random_state=42, **leiden_kwargs):
        '''
        Wrapper to run leiden clustering on self.adata

        from_sam : whether to use the connectivities generated by SAM
            or the default connectivities (those generated by sc.pp.neighbors)
        '''
        sc.tl.leiden(
            self.adata, 
            partition_type=leidenalg.RBConfigurationVertexPartition,
            adjacency=(self.adata.obsp['connectivities'] if from_sam else None),
            resolution=resolution, 
            use_weights=True,
            random_state=random_state,
            **leiden_kwargs
        )


    def calculate_ari(self, ground_truth_label, n_random_states=3, res=0.2):
        '''
        Measure the ARI and AMI for Leiden clustering at a range of resolutions
    
        ground_truth_label : the name of the column in self.adata.obs 
            to use as the ground-truth labels (must be a semicolon-separated list of labels)

        res: the sampling rate (in log10) of the leiden resolution
            0.1 is probably optimal; 0.2 is better for quick plots
        '''
        
        verbosity = sc.settings.verbosity
        sc.settings.verbosity = 1

        leiden_cluster_id = '_leiden_cluster_id'

        resolutions = 10**(np.arange(-1, 2.5, res))
        random_states = np.arange(42, 42 + n_random_states)

        Result = collections.namedtuple(
            'result', 
            ['resolution', 'random_state', 'num_clusters', 'median_cluster_size', 'ari', 'ami']
        )

        # only use targets that are in a single ground-truth cluster
        mask = self.adata.obs[ground_truth_label].str.split(';').apply(len) == 1

        results = []
        for resolution in resolutions:
            for random_state in random_states:
                self.run_leiden(resolution, key_added=leiden_cluster_id, random_state=random_state)

                d = pd.DataFrame()
                d['predicted_label'] = self.adata.obs[mask][leiden_cluster_id]
                d['ground_truth_label'] = self.adata.obs[mask][ground_truth_label].str.split(';')
                d = d.explode('ground_truth_label')
                d = d.loc[(d.ground_truth_label != 'none') & (~d.ground_truth_label.isna())]

                result = Result(
                    resolution=resolution,
                    random_state=random_state,
                    num_clusters=len(set(self.adata.obs[leiden_cluster_id])), 
                    median_cluster_size=self.adata.obs[leiden_cluster_id].value_counts().median(),
                    ari=adjusted_rand_score(d.ground_truth_label, d.predicted_label),
                    ami=adjusted_mutual_info_score(d.ground_truth_label, d.predicted_label),
                )
                results.append(result)
        
        sc.settings.verbosity = verbosity
        return pd.DataFrame(data=results)


    def calculate_kclique_metrics(
        self, drop_largest=False, max_clique=2, n_random_states=3
    ):
        '''
        Calculate k-clique metrics at a range of Leiden resolutions
        NOTE: lots of duplicated code here from calculate_ari
        '''
        corum_standard = ground_truth_labels.load_corum_standard(drop_largest)
        leiden_cluster_id = '_leiden_cluster_id'

        resolutions = 10**(np.arange(-1, 2.5, .2))
        random_states = np.arange(42, 42 + n_random_states)

        Result = collections.namedtuple(
            'result', 
            [
                'resolution', 
                'random_state', 
                'num_clusters', 
                'median_cluster_size',
                'grand_f1_score', 
                'cumulative_precision'
            ]
        )

        results = []
        for resolution in resolutions:
            for random_state in random_states:
                self.run_leiden(resolution, key_added=leiden_cluster_id, random_state=random_state)

                leiden_clusters = pd.DataFrame(
                    self.adata.obs.groupby(leiden_cluster_id)['target_name'].apply(list)
                )
                leiden_clusters = leiden_clusters['target_name'].to_list()

                comp = complex_comparison.ComplexComparison(
                    gold_standard=corum_standard, clusters=leiden_clusters, max_clique=max_clique
                )
                result = Result(
                    resolution=resolution, 
                    random_state=random_state,
                    num_clusters=len(set(self.adata.obs[leiden_cluster_id])), 
                    median_cluster_size=self.adata.obs[leiden_cluster_id].value_counts().median(),
                    grand_f1_score=comp.clique_comparison_metric_grandf1score(),
                    cumulative_precision=comp.clique_comparison_metric()[2]['cumulative_precision']
                )
                results.append(result)
        
        return pd.DataFrame(data=results)


    def run_agglomerative(
        self, 
        distance_threshold, 
        method='umap',
        n_umap_components=10, 
        linkage='ward', 
        affinity='euclidean',
        key_added='agg_cluster_id'
    ):
        '''
        Implements an unconventional clustering method: 
        agglomerative clustering on a high-dimensional UMAP embedding
        '''

        # generate a high-dimensional UMAP embedding
        if method == 'umap':
            sc.tl.umap(
                self.adata, 
                n_components=n_umap_components,
                min_dist=0.0,
                init_pos='spectral', 
                random_state=42
            )
            X = self.adata.obsm['X_umap']

        # use all of the PCs
        if method == 'pca':
            X = self.adata.obsm['X_pca']
        
        model = sklearn.cluster.AgglomerativeClustering(
            linkage=linkage,
            affinity=affinity,
            n_clusters=None,
            distance_threshold=distance_threshold,
        )
        model.fit(X)

        self.adata.obs[key_added] = [str(label) for label in model.labels_]
        print('Found %d clusters' % len(set(model.labels_)))


    def plot_sankey(
        self, 
        ground_truth_label, 
        predicted_label, 
        ground_truth_label_order=None, 
        predicted_label_order=None,
        flip=False
    ):

        obs = self.adata.obs.copy()
        mask = obs[ground_truth_label] != 'none'
    
        if ground_truth_label_order:
            ignored_labels_mask = obs[ground_truth_label].isin(ground_truth_label_order)
            if ignored_labels_mask.sum():
                print('Warning: dropping labels not found in ground_truth_label_order')
            mask = mask & ignored_labels_mask

        colormap = {}
        colors = SCATTERPLOT_COLORS
        obs = obs.loc[mask].copy()

        labels =obs[ground_truth_label].unique()
        colormap.update({label: colors[ind % len(colors)] for ind, label in enumerate(labels)})

        labels = obs[predicted_label].unique()
        colormap.update({label: colors[ind % len(colors)] for ind, label in enumerate(labels)})

        if flip:
            left_label, right_label = ground_truth_label, predicted_label
            left_label_order, right_label_order = ground_truth_label_order, predicted_label_order
        else:
            left_label, right_label = predicted_label, ground_truth_label
            left_label_order, right_label_order = predicted_label_order, ground_truth_label_order

        sankey.sankey(
            obs[left_label], 
            obs[right_label], 
            leftLabels=left_label_order,
            rightLabels=right_label_order,
            colorDict=colormap
        )
        return colormap


    def plot_umap(
        self, 
        color_label, 
        min_dist=0.0, 
        init_pos='spectral',
        random_state=42, 
        palette='tab10',
        ax=None,
        **umap_kwargs
    ):
        '''
        '''
        sc.tl.umap(
            self.adata, 
            init_pos=init_pos, 
            min_dist=min_dist,
            random_state=random_state,
        )
        sc.pl.umap(
            self.adata, 
            color=color_label, 
            groups=None, 
            edges=False, 
            alpha=0.7, 
            palette=palette,
            ax=ax,
            **umap_kwargs
        )


    def calculate_distance_matrix(self, metric='euclidean', n_pcs=None, **preprocessing_kwargs):
        '''
        metric : the distance metric to use
        n_pcs : the number of PCA components to use for calculating the distance matrix
            If None, the full data matrix (self.adata.X) is used
        preprocessing_kwargs : kwargs for self.preprocess
        '''

        # redo the preprocessing (scaling, log1p, PCA) 
        # to be sure the data matrix is what we think it is
        self.preprocess(n_pcs=n_pcs, **preprocessing_kwargs)

        if n_pcs is not None:
            X = self.adata.obsm['X_pca'].copy()
        else:
            try:
                X = self.adata.X.toarray()
            except AttributeError:
                X = self.adata.X.copy()
    
        dists = sklearn.metrics.pairwise_distances(X, metric=metric)
        if metric == 'correlation':
            dists = 1 - dists

        return dists


    def calculate_paris_hierarchy(self, leiden_cluster_column, shuffled=False):
        '''
        Hierarchically cluster the (presumably high-resolution) Leiden clusters 
        using the Paris algorithm

        leiden_cluster_column : the column in self.adata.obs containing the ids of the clusters
        to be hierarchically clustered (these are the Leiden clusters at resolution = 30)

        # these are the leiden clusters that Manu used for the full dataset
        leiden_cluster_column = 'cluster_id_leiden_res30_seed50'

        # the leiden clusters for the pub-ready-only dataset 
        # (excluding 70 cell lines in the 'full' dataset)
        leiden_cluster_column = 'cluster_id_leiden_res30_seed12'

        aside: using LouvainHierarchy doesn't yield a pretty dendrogram, 
        because the merged cluster distances are simply the node depth
        '''

        adj = self.adata.obsp['connectivities'].toarray()
        leiden_labels = self.adata.obs[leiden_cluster_column].values.copy()
        unique_leiden_labels = list(np.unique(leiden_labels[pd.notna(leiden_labels)]))
        n_leiden_labels = len(unique_leiden_labels)

        if shuffled:
            np.random.shuffle(leiden_labels)

        # calculate the edge weights between the leiden clusters by summing the adjacencies 
        # between all pairs of targets shared between each pair of clusters
        # (this is what the paris algorithm does)
        leiden_cluster_adjacencies = np.zeros((n_leiden_labels, n_leiden_labels))
        for row_ind in range(n_leiden_labels):
            for col_ind in range(row_ind + 1, n_leiden_labels):
                row_label = unique_leiden_labels[row_ind]
                col_label = unique_leiden_labels[col_ind]
                weight = adj[leiden_labels == row_label, :][:, leiden_labels == col_label].sum()
                leiden_cluster_adjacencies[row_ind, col_ind] = weight
                leiden_cluster_adjacencies[col_ind, row_ind] = weight

        # use the paris algorithm to hierarchically cluster the leiden clusters
        paris = sknetwork.hierarchy.Paris()
        self.full_dendrogram = paris.fit_transform(leiden_cluster_adjacencies)

        # the 'subclusters' are now the high-resolution Leiden clusters 
        # that we have just hierarchically clustered
        self.subcluster_column = leiden_cluster_column


    def assign_dendrogram_cluster_ids(self, dendrogram_labels, key_added=None):
        '''
        Map the dendrogram cluster ids to targets
        Because the dendrogram clusters are clusters of leiden clusters, 
        this requires mapping the dendrogram cluster ids to their Leiden cluster id
        '''
        if key_added is None:
            key_added = 'dendrogram_cluster_id'

        # the dendrogram labels are in the order of the sorted unique leiden labels
        # (that is, the ids of the Leiden clusters that were hierarchically clustered)
        # (which np.unique returns)
        leiden_labels = self.adata.obs[self.subcluster_column].values
        unique_leiden_labels = list(np.unique(leiden_labels[pd.notna(leiden_labels)]))

        # determine the dendrogram label for each target
        self.adata.obs[key_added] = None
        for ind, row in self.adata.obs.iterrows():
            leiden_label = row[self.subcluster_column]
            if pd.isna(leiden_label):
                continue
            self.adata.obs.at[ind, key_added] = (
                dendrogram_labels[unique_leiden_labels.index(leiden_label)]
            )
        self.adata.obs[key_added] = self.adata.obs[key_added].astype(pd.CategoricalDtype())


    def plot_full_dendrogram(self, using='svg'):
        '''
        '''
        # the labels for the full dendrogram
        full_dendrogram_cluster_ids, full_dendrogram = sknetwork.hierarchy.cut_straight(
            self.full_dendrogram, threshold=0.0, return_dendrogram=True
        )
        self.assign_dendrogram_cluster_ids(
            full_dendrogram_cluster_ids, key_added='full_dendrogram_cluster_id'
        )

        # construct leaf names from all target names in each leaf
        leaf_names = []
        obs = self.adata.obs.copy()

        # this is the order the leaf names must be in for svg_dendrogram
        for dendrogram_cluster_id in np.unique(full_dendrogram_cluster_ids):
            obs_crop = obs.loc[obs.full_dendrogram_cluster_id == dendrogram_cluster_id]
            
            # the target names in this leaf
            target_names = obs_crop['target_name'].tolist()

            # the leiden cluster corresponding to this leaf 
            # (because we are using the full dendrogram, this is 1-1 by definition)
            leiden_cluster_id = obs_crop[self.subcluster_column].iloc[0]
            
            name = ('%s: ' % leiden_cluster_id) + (', '.join(target_names))
            leaf_names.append(name)

        # SVG of the full dendrogram labeled with the list of target names in each leaf node
        if using == 'svg':
            svg = sknetwork.visualization.svg_dendrogram(
                full_dendrogram, 
                rotate=True, 
                names=leaf_names, 
                n_clusters=5, 
                height=1600, 
                width=600,
                font_size=10
            )
            return svg

        # plot the full dendrogram using sp
        else:
            plt.figure(figsize=(6, 12))
            ax = plt.gca()
            _ = sp.cluster.hierarchy.dendrogram(
                full_dendrogram, 
                orientation='top', 
                color_threshold=0.0,
                above_threshold_color='gray',
                labels=None,
                ax=ax
            )
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.get_xaxis().set_ticks([])
            ax.grid(False)


    def cut_dendrogram(self, cut_threshold, key_added=None):
        '''
        '''
        cut_dendrogram_cluster_ids, cut_dendrogram = sknetwork.hierarchy.cut_straight(
            self.full_dendrogram, threshold=cut_threshold, return_dendrogram=True
        )
        self.assign_dendrogram_cluster_ids(
            cut_dendrogram_cluster_ids, key_added=(key_added or 'cut_dendrogram_cluster_id')
        )
        return cut_dendrogram_cluster_ids, cut_dendrogram


    def plot_dendrogram_umap(self, cut_threshold, ground_truth_label=None, orientation='top'):
        '''
        '''
        cut_dendrogram_cluster_ids, cut_dendrogram = self.cut_dendrogram(cut_threshold)

        dendrogram_labels = None
        if ground_truth_label is not None:
            obs = self.adata.obs.copy()
            obs = obs.loc[obs[ground_truth_label] != 'none']

            dendrogram_labels = []
            for cluster_id in np.unique(cut_dendrogram_cluster_ids):
                
                # the most common labels in a cluster
                n = (
                    obs.loc[obs['cut_dendrogram_cluster_id'] == cluster_id][ground_truth_label]
                    .value_counts()
                )
                if not n.sum():
                    label = 'none'
                else:
                    label = ', '.join([
                        '%d%% %s' % (100*n.iloc[ind]/n.sum(), n.index[ind]) for ind in [0, 1]
                    ])
                label += ' (n = %d)' % n.sum()
                label = '%s: %s' % (cluster_id, label)
                dendrogram_labels.append(label)

        fig, axs = plt.subplots(1, 2, figsize=(12, 5))
        ax = axs[1]
        _ = sp.cluster.hierarchy.dendrogram(
            cut_dendrogram, 
            orientation=orientation, 
            color_threshold=0.0,
            above_threshold_color='gray',
            labels=dendrogram_labels,
            ax=ax,
        )
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.grid(False)
        # ax.get_yaxis().set_ticks([])

        # ax.axis('off')
        ax = axs[0]
        sc.pl.umap(
            self.adata, 
            color='cut_dendrogram_cluster_id', 
            alpha=0.7, 
            palette='tab20',
            legend_loc='on data',
            legend_fontsize=20,
            legend_fontoutline=2,
            add_outline=False,
            title='',
            ax=ax,
        )

        return fig