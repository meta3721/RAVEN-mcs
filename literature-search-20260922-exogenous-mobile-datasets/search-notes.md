# Search Notes

## Safe Queries Used

- OpenSense Zurich mobile air quality tram dataset public GPS PM
- Apte high-resolution air pollution mapping Google Street View Oakland dataset public
- Breathe London mobile monitoring dataset download GPS NO2
- mobile crowdsensing dataset upload success packet loss client availability trace public
- mobile PM2.5 GPS trajectory dataset zenodo taxi bicycle
- WorldPop population count 100m geotiff public dataset
- London Air Quality Network LAQN open data stations NO2
- Hasenfratz Pushing the Spatio-Temporal Resolution Limit PerCom 2014 DOI
- S&M-HSTPM2d5 dataset descriptor paper DOI
- Guangzhou taxi NO2 PM2.5 GPS dataset public download 314 taxis
- Hyperlocal environmental data mobile platform City Scanner Scientific Data Wang 2023 DOI

## Sources Checked

- Zenodo records 10.5281/zenodo.3298842, 10.5281/zenodo.3355208, 10.5281/zenodo.7961851, 10.5281/zenodo.4028129, 10.5281/zenodo.1287751
- IEEE DOI 10.1109/percom.2014.6813946 and DBLP PerCom entry
- ACS ES&T 10.1021/acs.est.7b00891
- Google Earth Engine Air View catalog
- EDF Breathe London methodology page and QA/QC protocol
- data.smartdublin.ie Air View Dublin
- Scientific Data 10.1038/s41597-023-02425-3
- WorldPop population-count listing
- London Air API
- RepOD 10.18150/myfysj
- arXiv 2409.12412 and 2412.17831

## Excluded Sources

- Policy-excluded or low-quality sources: an MDPI Sensors PDF on Wi-Fi upload selection appeared in discovery and was not scored or recommended.
- Other exclusions: PEMS-BAY and similar loop-detector series were not reopened; they supply fixed-sensor speed, not mobility-derived opportunity or upload state. CHAP gridded pollution products are model or satellite concentration maps, so they are not a label-free mass and not a mobile trace. PePa Ping and CRAWDAD SIGCOMM 2009 Bluetooth logs were screened as network or encounter traces and dropped because they do not share a sensing key. A Birmingham npj campaign was screened as a small local deployment without a reusable corpus page.

## Unknowns

- Papers not accessible: the S&M-HSTPM2d5 record cites a data descriptor that this search did not identify. Hasenfratz Pervasive and Mobile Computing 2015 is named on the UFP Zenodo page and was not given its own scored row.
- Venue status not verified: OSTLUFT download terms were not audited; the OpenSense gas record only names www.ostluft.ch as reference data.
- Missing benchmark details: Air View and Breathe London licenses were not re-read line by line. Guangzhou raw files were not found. City Scanner device-status streaming is described in the paper; the published table fields do not include upload success.

## Handoff Notes

- For writing: cite a dataset page if a trace is adopted. Do not describe WorldPop as a mobile crowdsensing dataset.
- For idea optimization: not applicable.
- For direction scouting: the open public gap is co-located measured upload, not another concentration corpus.
- For experiment design: freeze the mass before any error is computed; keep usable-update labeled synthetic unless a same-key upload log appears.
- For review: a dataset swap alone does not answer the split-derived target defect.
