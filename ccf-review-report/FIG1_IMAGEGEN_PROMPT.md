# 图一候选草图：内置生成提示

模式：内置 image_gen；用途：scientific-educational / paper mechanism figure。仅生成一张候选位图，不改规范图或论文。无输入图片，不上传范文PDF或完整论文。

官方核验：https://learn.chatgpt.com/docs/image-generation 明确写明内置图像生成使用 gpt-image-2；本会话存在 image_gen__imagegen。此前“型号无法核实”的阻碍已解除。未使用付费API/CLI，不要求 OPENAI_API_KEY。

## 完整发送提示

```text
Create ONE original scientific paper mechanism figure, a candidate raster concept for Figure 1 of RAVEN-MCS, for a full-width IEEE two-column paper. White background, wide landscape approximately 2.2:1. This is a computation graph, not a presentation slide. Use clear concrete objects, compact exact English labels, simple consistent flat vector-style line icons, and generous whitespace. No headline banner. All three subfigure titles aligned BELOW the drawing.

Scientific message: Sequential sensing opportunity R, observation O, and usable model-update delivery U change what arriving data represent. RAVEN-MCS reconstructs target reference mass over atomic sensing units, then calibrates that statistical reference into executable client weights on the available finite-window support. Deployment target μ, corrected reference β̂_r, and executable weights α*_r are distinct. Give the central β̂_r → P2 → α*_r transformation the greatest visual weight.

(a) LEFT, approximately 25% width, title "Sensing and usable updates". Draw a small urban road / space-time grid with a mobile sensing device, then a small LOCAL table of measurement records. Label "Opportunity R" and "Observation O". Devices are sensing carriers, not necessarily FL clients; small note "Carrier illustration; clients are protocol-defined". Show "Local normalized training" on those records producing MODEL UPDATE packets u_k,r, not uploads of raw observations. Draw a small time line with "Window opens", "Window closes", two packets before close and one faded packet after close labelled "Late". "Usable U" means computation + transmission finish before close with admissible staleness. Mark positive-mass usable clients "A_r: U = 1, m > 0". Keep raw measurements visibly local.

(b) CENTER, approximately 50% width, title "Reference reconstruction and feasible calibration".
Exact main arrow chain: "Selection histories + target information" → "Reference reconstruction" → a small BLUE bar vector "Corrected reference β̂_r" → ONE emphasized operator "P2" / "Constrained calibration" → a small TEAL bar vector "Executable weights α*_r ∈ C_r".
In the reference reconstruction operator include ONLY two concise explanatory lines: "Opportunity / observation correction: m" and "Usability correction: β̂ ∝ m d". Selection probabilities come from pre-outcome histories; opportunity estimates are lagged. A small input label "Design: fixed before window" feeds reconstruction, not a Gate. No Gate switch.
Attach clearly labelled arrows INTO P2 for:
- "Available clients A_r" and a small client-by-group composition matrix labelled "Group composition M_r";
- a distinct target mass object labelled "Deployment target μ";
- a simple feasible-region shape labelled "Caps + effective support C_r";
- a state input "Current debt Q_r; lagged V_r; staleness".
Inside or immediately under P2 add the two short roles "Reference fidelity" and "Group alignment". P2 is one full calibration program; do NOT draw separate instantaneous-calibration or projection stages.
The BLUE β and TEAL α small vectors have no numerical axes or values and are explicitly schematic. Their heights may differ. Do not imply β must lie in the feasible region or that M_r α*_r equals μ.
Represent the auxiliary sensing-side correction as feeding local normalized training as well as the reference mass m, using a clearly labelled connector if needed, without sending raw measurement tables to the server.
The MODEL UPDATE packets u_k,r must travel on a SEPARATE labelled route to the aggregation server, bypassing P2. Current update coordinates/norms/directions are NOT inputs used to assign weights.

(c) RIGHT, approximately 25% width, title "Aggregate and advance state".
A modest server icon labelled "Weighted aggregation" consumes the executable weights AND the separate "Usable model updates u_k,r" stream, yielding "Updated model θ_(r+1)". Optionally a small schematic completion grid, no numbers or claims of better accuracy.
The next operation AFTER aggregation is "Debt + lagged-state update", with a recognizable group-by-group under-service ledger (table/list, never money icon). Its input is aggregated composition "ω_r = M_r α*_r", with μ and Q_r. Its output is "Next debt Q_(r+1)" and updated lagged histories. Use a dashed feedback route, labelled "Next window", returning the next debt to the next P2 state input and updated histories to next reference reconstruction. No arrow implying debt update before aggregation. Current Q_r and next Q_(r+1) must have different labels.
Show active-window flow; do not invent a fallback controller or an optimization guarantee.

Arrow semantics: solid arrows = current-window data/state inputs, dashed arrows = next-window state feedback. Give a small concise legend with those two line samples. Every arrow has identifiable source, destination, and scientific meaning. Avoid crossings through text. A long separate usable-update stream may route along an outer edge, while the feedback has its own lane.

Style: a coherent set of original minimal line icons; low-saturation blue for reconstructed mass, teal for feasible weights, neutral grey for sensing/server, muted ochre for group under-service. Dark high-contrast text, restrained highlights centered on P2, readable at about 180 mm paper width. Short labels, no long prose cards, no decorative shadows, no 3D, no logos, no invented modules or privacy mechanisms, no empirical numbers, no claim that missing sensing support is created. Keep the map, vectors and ledger explicitly schematic. Do not copy any published figure's specific arrangement or artwork. Return just one finished candidate diagram.
```
