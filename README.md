# 2021 OpenCell figures
__October 2021__

This repo contains the code and data used to generate the figures for the [2021 OpenCell preprint](https://www.biorxiv.org/content/10.1101/2021.03.29.437450v1). It was developed by [Keith Cheveralls](https://github.com/keithchev) and [Kibeom Kim](https://github.com/kkimatx) in the Leonetti group at the Chan Zuckerberg Biohub. 


## What's in this repo
### `data/`
This directory contains various external and processed datasets required to make the figures. Note that some of these datasets are from external sources; these are found in the `data/external/` subdirectory. The remaining datasets are all original datasets generated by or derived from the OpenCell project. Note that some datasets, including the full IP-MS interaction dataset and the matrix of target localization encodings, are too large to host on GitHub. These datasets are available [on FigShare](https://figshare.com/projects/OpenCell_proteome-scale_endogenous_tagging_enables_the_cartography_of_human_cellular_organization/123844). 


### `notebooks/`
These are Jupyter notebooks that document how the figures were generated using the Python modules in `scripts/`. The notebooks used for each figure panel are [specified below](#where-to-find-the-code-and-data-used-to-generate-each-figure). These notebooks are the primary documentation 
for how the scripts in `scripts/` were used for analysis and figure generation. 


### `scripts/`
These are Python modules that contain the bulk of the code used for data analysis and figure generation. They are used directly by the Jupyter notebooks discussed above. Please note that these scripts are explicitly written for, and specific to, the OpenCell project. They are __not__ intended to form a stand-alone or general-purpose Python package.

- __`scripts/annotation_comparisons/`__ These modules are used to compare manual localization annotations from OpenCell to those from the HPA and from a yeast dataset. 

- __`scripts/biophysical_properties/`__ This module calculates or retrieves various protein biophysical properties for all OpenCell targets and interactors, including hydrophobicity and disorder scores.  

- __`scripts/cytoself_analysis/`__ These modules analyze the encodings of protein localization patterns generated by the cytoself model from the OpenCell microscopy dataset. 

- __`scripts/interactome_markov_clustering/`__ This documents how the Markov clustering is used to delineate the mass-spec 'communities.'

- __`scripts/interactome_paris_clustering/`__ This documents how the interaction communities are themselves clustered using a hierarchical clustering algorithm to yield a hierarchical representation of the interactome. 

- __`scripts/interactome_precision_recall/`__ This module documents how estimates of precision and recall are obtained for our mass-spec interactions. 

- __`scripts/external/`__ These are external dependencies that were either modified by us for a specific purpose or are not available as pip-installable packages.

- __`scripts/pyseus/`__ This module is technically an external dependency; it is a package of analysis and visualization methods that we developed for analyzing our mass-spec interaction data. It is not yet pip-installable, so it is included here. 


## Where to find the code and data used to generate each figure
Here we provide links to the notebook sections or Python scripts that were used to generate the data and/or the graphics underlying each figure panel. Note that, for figure panels that are direct visualizations (e.g., bar or scatterplots) of data found in a supplementary table, we refer directly to the relevant supplementary table itself. Also, in some cases, the same data or graphic is used in slightly different forms in multiple figures; when this occurs, we try to indicate this transparently without replicating the same links.

### Figure 2
__2C-D:__ Example of an interactome community and its core clusters, and an overview of all interactome communities. These graphics were generated using Cytoscape directly from the cluster memberships in Supp. Table 5. Core cluster membership is generated by second-step Markov clustering documented [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/ppi_analysis/mcl_second_clustering.ipynb). 

__2E:__ PubMed citation count vs protein expression level. Refer to Supp. Table 2 for expression levels.

__2F:__ Interaction network for SCAR/WAVE. The network visualization was generated using Cytoscape directly from the protein-protein interactions in Supp. Table 4. 

__2G:__ Heatmaps and volcano plots for RAVE complex. Generated using Plotly directly from the protein-protein interactions in Supp. Table 4.


### Figure 3
__3B:__ Sankey diagram comparing OpenCell and HPA localization annotations. This is [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/HPA-OC-comparison.ipynb#Sankey-for-all-targets).

__3D:__ UMAP of target localization encodings. This is generated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-figures.ipynb#UMAP-of-target-localization-encodings). Please note that this same UMAP is used in many subsequent figures, with different colormaps to indicate localization annotations, cluster memberships, etc. 


### Figure 4
__4A:__ ARI curves for localization-based Leiden clustering. These are calculated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-performance.ipynb#Plots-of-ARI-vs-Leiden-resolution).

__4B:__ Sankey diagram of low-resolution Leiden clusters vs manual annotations. This is generated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-performance.ipynb#sankey-plot-comparing-oc-annotations-to-leiden-clustering). 

__4C:__ UMAP of localization encodings colored by high-resolution localization clusters. For the UMAP, see Figure 3D above. The Leiden clustering is performed [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-figures.ipynb#Leiden-clustering). 

__4D-E__: 2D histograms of interaction stoichiometry vs localization similarity. The interaction stoichiometries are found in Supp. Table 4 and the matrix of localization similarities is generated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-figures.ipynb#Calculate-the-matrix-of-target-target-localization-similarities).

__4G:__ Proportion of interacting target pairs by localization similarity. This uses the same matrices of localization similarities and protein-protein interactions as in Figure 4D-E above. 

__4H:__ FAM241A de-orphaning. The ranked similarities are plotted directly from the matrix of localization similarities (see Figure 4D-E above) and the heatmap of interactions was generated using Plotly from Supp. Table 4. 


### Figure 5
__5A:__ Interactome hierarchy. The interaction communities are clustered using the Paris hierarchical clustering algorithm [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/ppi_analysis/paris_hierarchy.ipynb). 

__5B:__ Composition of interactome hierarchy branches. Refer to Supp. Table 2 for protein annotations and Supp. Table 5 for protein membership in branches.

__5C:__ Box-whisker plots of biophysical properties by branch. The biophysical properties are calculated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/biophysical-properties-in-clusters.ipynb).

__5D-E__: Within-spatial-cluster mean disorder and percent RNA-BPs. The disorder scores are retrieved from the IUPRED API and the within-cluster means are calculated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/biophysical-properties-in-clusters.ipynb#Plot-the-distribution-of-within-cluster-means). 


### Figure S1
__S1B__: Choice of tag terminus. Generated directly from Supp. Table 3.

__S1C__: Number of detected interactors vs input material.

__S1D__: Distribution of GO annotations. 


### Figure S2
__S2A__: Target success rate. Generated directly from Supp. Table 3. 

__S2B__: RNA vs protein abundance. Generated directly from Supp. Table 2.

__S2C-E__: Properties of successful tags. Generated directly from Supp. Table 3. 


### Figure S4
__S4B__: Precision-recall curve for interactome clustering. This is calculated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/ppi_analysis/pr_curve.ipynb).

__S4C-D__: CORUM based recall and co-localization based precision for various datasets. This is calculated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/ppi_analysis/precision_recall.ipynb).

__S4E__: Precision-recall for interactions in both Bioplex 3.0 and OpenCell. See Figure S4B. 

__S4F__: Interaction network compression rates. The compression rates are calculated according to [Royer et al](10.1371/journal.pone.0035729).

__S4G__: Number of interactions unique to OpenCell. Refer to Supp. Table 4. 

__S4H__: Overlapping GO annotations between interactors in high-stoichiometry vs low-stoichiometry interactions. Calculated using Supp. Table 4. 

__S4I__: Clustering F1 score vs MCL inflation. This is calculated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/ppi_analysis/humap_cluster_comparison.ipynb).


### Figure S7
__S7B__: Heatmap of multi-localizing targets. This is generated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/multilocalizing-targets-heatmap.ipynb).

__S7C__: Sankey diagram of OC-HPA discrepancies. This is generated [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/HPA-OC-comparison.ipynb#Sankey-for-manually-curated-discrepant-targets). 


### Figure S8
__S8A__: Cluster size vs clustering resolution. The localization cluster sizes are calculated along with the ARI curves [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-performance.ipynb#Plots-of-ARI-vs-Leiden-resolution). 

__S8B-C__: Additional examples of high-resolution localization clusters. See Figure 4C.


### Figure S9
__S9A__: Localization-based hierarchical clustering. The hierarchy is obtained by clustering the high-resolution localization clusters using the Paris algorithm [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-figures.ipynb#Paris-hierarchy-from-the-Leiden-clusters). 

__S9B__: Interactome hierarchy. See Figure 5A. 


### Figure S10
__S10A-E__: GO enrichment in hierarchy branches. The enrichement analysis is performed by using the Panther API. An example of how this API is used (for the localization clusters) is [here](https://nbviewer.jupyter.org/github/czbiohub/2021-opencell-figures/blob/master/notebooks/localization_clustering/clustering-figures.ipynb#Enriched-GO-terms-in-the-Leiden-clusters%2C-modules%2C-and-branches). 

__S10F-G__: Additional biophysical properties by interactome hierarchy branch. See Figure 5C. 


### Figure S11
__S11A-C__: Protein abundance, disorder scores, and number of interactors for RNA-binding proteins. Refer to Supp. Table 2 and Supp. Table 4.

__S11D__: Protein abundance vs number of interactors. Refer to Supp. Table 2 and Supp. Table 4. 

__S11E__: Within-spatial-cluster mean hydrophobicity. See Figure 5D-E. 


# License
Chan Zuckerberg Biohub Software License

This software license is the 2-clause BSD license plus a third clause
that prohibits redistribution and use for commercial purposes without further
permission.

Copyright © 2021. Chan Zuckerberg Biohub.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1.	Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2.	Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3.	Redistributions and use for commercial purposes are not permitted without
the Chan Zuckerberg Biohub's written permission. For purposes of this license,
commercial purposes are the incorporation of the Chan Zuckerberg Biohub's
software into anything for which you will charge fees or other compensation or
use of the software to perform a commercial service for a third party.
Contact ip@czbiohub.org for commercial licensing opportunities.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
