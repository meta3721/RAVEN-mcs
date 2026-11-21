import {Stack,Row,Grid,H1,H2,Text,Table,Button,Pill,Divider,useState,useHostTheme,useCanvasAction} from "cursor/canvas";

const root="C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/";
const report="C:/Users/szr/Desktop/record/1/ccfa-review-reports/submission-readiness-review.md";
const preservation=[
 ["正文结果表","7 → 7","全部tabular数值内容不变","正文8—12页"],
 ["补充结果表","23 → 23","数值不变；表XXVI仅动态引用替换","补充5—14页"],
 ["关键权重规则","完整保留","Count / Uniform / 投影 / 债务变体 / Inst-Cal / RAVEN，含耗时","正文表IV，第11页"],
 ["组件消融","40 / 40单元匹配","数值打印精度与显著性标记均匹配CSV；两幅重复图可删","正文表V，第11页"],
 ["主文编号公式","43 → 43","38个带标签环境内容不变；附录证明抽查链条仍在","正文VI与附录A/B"],
 ["不利结果与条件","保留","训练均值不足、Use不显著、默认Debt小、覆盖0.750、真实U未测量","正文8、10—12页及补充"],
 ["开发证据身份","保留","47.01% / 10.16%为集中式开发收益；U-Air −0.96%，均非RAVEN收益","补充表XXIX与图8"],
 ["证据定位入口","退步","具体目录与修正评分文件被抽象索引指代替代；早期包仍有UNLOCATED","正文13页Availability"]
];
const issues=[
 {id:"S1",origin:"继承问题",priority:"高",title:"U-Air图表支持/评分身份未闭合",where:"补充图5/6，第7页；表XVIII，第9页",fact:"FedAsync组失配：图CSV 1.1223，表1.0451；RAVEN均为1.0924，比较排序会反转。FedAvg等也有差异。",meaning:"已确认展示不同，尚不能判定哪个错。可能涉及支持集或评分口径，图注未充分识别。",repair:"用已有运行记录统一身份，或明确两个不同对照；不能挑有利数值。默认不重训。",path:root+"appendix.tex"},
 {id:"S2",origin:"继承问题",priority:"高",title:"附录错误概括定理前提",where:"附录H，第9页；正文命题2/3",fact:"附录称重建仅需A5，正文命题2需A1—A3；命题3还需A1、A4等。",meaning:"活跃支持正性不能替代理想识别和正确比率。主要证明链仍在，概括句需要修正。",repair:"把附录条件映射改为与命题一致，只认定审计真正检查到的子条件。",path:root+"appendix.tex"},
 {id:"S3",origin:"压缩退步及旧缺项",priority:"中高",title:"关键结果可追溯入口变弱",where:"正文13页Availability；证据包数字索引",fact:"后期修正W1、Adam、集中度、学习和几何仅指向未明确入口的revision evidence record；现用3.44/1.32 pp在旧包标为UNLOCATED。",meaning:"本地文件存在，不等于审稿人能从交付包找到和复核。原稿访问问题也未完全解决。",repair:"提供随投稿可访问的清单，标明文件、对照和修正口径；正文保留一个短入口即可。",path:root+"main.tex"},
 {id:"S4",origin:"继承问题",priority:"中",title:"Design/Gate仍有术语歧义",where:"补充表XXVI图注，第12页",fact:"仍称“The gate sets Design on…”，其他位置却明确覆盖Gate不切换Design。",meaning:"可能只是离线支持规则的泛称，不能据此断言代码行为冲突。",repair:"统一为离线支持规则/预窗口配置，保留输入可用时点。",path:root+"appendix.tex"},
 {id:"S5",origin:"提交准备未完成",priority:"提交前",title:"作者占位符与规则核准",where:"正文/补充首页；期刊投稿要求",fact:"作者、单位、邮箱仍含****；14/14已满足用户预算，但本轮未闭环当前TMC专门页限/补充政策。",meaning:"不把历史规则或其他期刊规则当作现行TMC标准。",repair:"按实际稿型完成作者或匿名信息，核准官方页限和补充要求。",path:root+"main.tex"}
];
const scores=[
 ["问题与贡献界定","3.5 / 5","感知单元、信息边界、窗口可实现性清楚","较高"],
 ["方法独立增量","2.5 / 5","扣分：完整目标相对简单投影价值不足；改善：界定不可替代能力或收窄承诺","中等"],
 ["理论承接","3 / 5","扣分：主要为条件性正确性，S2条件冲突；改善：修映射并匹配主张强度","中等偏高"],
 ["实验识别创新","2.5 / 5","扣分：组件/任务收益有限；改善：闭合S1，主张与实际识别效应一致","较高"],
 ["一致性与可复核性","2.5 / 5","扣分：S1—S3；改善：图表身份、条件、交付索引闭合","高"],
 ["本轮关键证据保留","4 / 5","表格、负结果和证明链保留；证据入口变弱","高"]
];

export default function SubmissionReadiness(){
 const theme=useHostTheme(); const action=useCanvasAction(); const [selected,setSelected]=useState("S1");
 const item=issues.find(x=>x.id===selected)||issues[0];
 const open=(path:string)=>action({type:"openFile",path});
 return <Stack gap={24} style={{padding:24,maxWidth:1420,margin:"0 auto",background:theme.bg.editor,color:theme.text.primary}}>
  <Stack gap={8}><Text size="small" tone="secondary">RAVEN-MCS · 投稿就绪与压缩保留审查 · 2026-10-17</Text>
   <H1>核心证据总体保住了，当前文件仍应暂缓提交</H1>
   <Text weight="semibold" style={{color:theme.accent.primary}}>不需要扩回18页。先修图表身份、假设概括和证据入口；科学独立增量仍是另一项评审风险。</Text>
   <Row gap={8} wrap><Button onClick={()=>open(report)}>完整审查</Button><Button variant="secondary" onClick={()=>open(root+"main.pdf")}>正文14页</Button><Button variant="secondary" onClick={()=>open(root+"supplemental.pdf")}>补充14页</Button></Row>
  </Stack>
  <Grid columns={2} gap={28}>
   <Stack gap={8}><H2>压缩验收</H2><Text>7张主表、23张补充表全部保留；40个消融单元独立匹配。没有发现删去不利结果或把理论条件升级成无条件保证。</Text><Text size="small" tone="secondary">比较范围：最后一轮18/18 → 14/14；不是最早稿到现稿的全历史差分。</Text></Stack>
   <Stack gap={8}><H2>绝对投稿判断</H2><Text>暂不建议直接提交。完整RAVEN部分端点不及简单投影，结构收益未稳定转成预测收益。这些是继承的科学问题，不能算作删页造成的退步。</Text><Text size="small" tone="secondary">14/14满足用户预算；当前TMC专门格式政策尚未闭环。没有新增实验。</Text></Stack>
  </Grid>
  <Divider/>
  <Stack gap={10}><H2>关键证据保留矩阵</H2><Text size="small" tone="secondary">来源：当前TeX/PDF、最后一轮压缩前源码、图表CSV。数字为保留数量，非论文效应量。</Text><Table headers={["对象","前后或核查结果","实质判断","定位"]} rows={preservation} striped/></Stack>
  <Stack gap={12}><H2>提交前问题：区分继承缺陷与压缩退步</H2><Row gap={8} wrap>{issues.map(x=><Pill key={x.id} active={x.id===selected} onClick={()=>setSelected(x.id)}>{x.id+" · "+x.priority}</Pill>)}</Row>
   <Text size="small" tone="secondary">{item.origin+" · "+item.where}</Text><H2>{item.title}</H2>
   <Grid columns={2} gap={24}><Stack gap={8}><Text weight="semibold">可核查事实</Text><Text>{item.fact}</Text><Text>{item.meaning}</Text></Stack><Stack gap={8}><Text weight="semibold">通过条件</Text><Text>{item.repair}</Text><Button variant="secondary" onClick={()=>open(item.path)}>查看对应源码</Button></Stack></Grid>
  </Stack>
  <Divider/><Stack gap={10}><H2>现稿分项判断</H2><Text size="small" tone="secondary">1—5分；不与历史分数求差，不代表接收概率。保留程度与绝对就绪分开解读。</Text><Table headers={["维度","分数","依据 / 改善条件","置信度"]} rows={scores} striped/></Stack>
  <Stack gap={8}><H2>最小修复顺序</H2><Text>S1身份溯源 → S2/S4几句条件与术语 → S3审稿可访问索引 → S5提交包核准。优先使用现有记录，不自动启动暂停的训练。</Text><Text>保护表IV—VII、Design两臂、负结果、覆盖失败单元和开发协议身份；不必恢复已由表V完整承接的重复消融图。</Text></Stack>
  <Divider/><Text size="small" tone="secondary">检查：28页提取与缩略目视，关键页放大，表/公式前后核查，40单元匹配，现有日志和字体检查。未做全部原始运行复算、形式化证明认证、全面外部引用核验或远端包访问验收。报告中逐项列出证据与修复责任。</Text>
 </Stack>;
}
