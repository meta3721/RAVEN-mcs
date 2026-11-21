import {Stack,Row,Grid,H1,H2,Text,Table,Pill,Button,Divider,useState,useHostTheme,useCanvasAction} from "cursor/canvas";
const root="C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/";
const report="C:/Users/szr/Desktop/record/1/ccfa-review-reports/experiment-narrative-review.md";
const issues=[
 {id:"N1",location:"City Scanner · 正文第9页",kind:"重排与合并",problem:"组对齐优势、其他方法预测领先、阶段标准未过、跨块因果边界连续挤在短段中。",keep:"FedAvg/TwoStage预测领先、实际收益和原门槛结论。",action:"每段回答一个问题，先给完整排序和效应，再集中交代该对照的适用范围。",line:1323},
 {id:"N2",location:"风险语义 · 正文第9页",kind:"删除重复性否定",problem:"证明不同风险响应后，又补一句not RAVEN prediction superiority，转向该实验并非用来检验的问题。",keep:"两种风险的响应差异、六场景复合/抵消结果与统计依据。",action:"解释本实验真正识别了什么；除非纠正附近错误主张，不反复追加全局预测优越性的否定。",line:1348},
 {id:"N3",location:"站点Design · 正文第10页",kind:"合并重复",problem:"预测优越性未建立在段首、表注、表后重复；U-Air反转也多次展开。",keep:"具体比较、Holm结论、Design两臂和反转数值。",action:"保留一个主要统计解释位置；图文各自解释独有机制信息。",line:1428},
 {id:"N4",location:"完整P2与投影 · 正文第11页",kind:"保留实质并拆段",problem:"结构、预测、耗时和逐点最优性审计被串为一段否定。",keep:"完整P2的真实取舍、误差量级及非精确认证性质。",action:"按结构/预测/成本解释；详细数值审计集中附录。写作不能补足完整方法采用价值。",line:1570},
 {id:"N5",location:"组件消融 · 正文第11页",kind:"中性化评价与去重",problem:"Use无显著性、Debt显著但tiny、区间内、未证明必要性接连出现。",keep:"效应、显著性与实际意义区间，不能把不显著说成等价。",action:"数字与区间替代主观tiny；按组件作用解释，必要性只归纳一次。",line:1587},
 {id:"N6",location:"City Scanner六臂 · 第11—12页",kind:"集中过程说明",problem:"主区间后追加不等价、非纯删除效应、所有轨迹仍保留三层说明。",keep:"不确定区间与floor改变边际，后者直接限制因果解释。",action:"突出结构保留率和主区间的各自含义；轨迹保留过程集中方法/附录，不用审计口吻收尾。",line:1636},
 {id:"N7",location:"敏感性与几何 · 正文第12页",kind:"按问题重组",problem:"不是最优界、不是预测保证、不是MNAR证据、不是预测实验等逐项叠加。",keep:"范围差别、开发与测试身份、真实诊断量。",action:"分为预测敏感性、可行支持、骨干能力；先解释实际发现，再保留必要的特定边界。",line:1648},
 {id:"N8",location:"更新与覆盖 · 第12—13页",kind:"分离独立问题",problem:"服务器更新、验证评分、识别、缺失日志、覆盖失败和真实U被写成一串限制。",keep:"Adam区间、覆盖0.750、真实U未测量及关键来源问题。",action:"每段一个问题，支持审计回到对应理论，覆盖来源集中说明，验证选择回到评分敏感性。",line:1758}
];
const protectedFacts=[
 ["学习基线","SensorScope/U-Air旧主模型未胜各自训练均值","保留数字；减少版本工作记录口吻"],
 ["完整方法取舍","投影更快且部分端点更好，完整准则另有结构收益","保留完整比较，不能写成全面领先"],
 ["真实场景排序","访问占用FedAvg预测最好，Pilot 2的TwoStage最好","保留所有方法；同时解释RAVEN的组优势"],
 ["组件与统计","Use无调整后显著性，默认Debt效果小","保留效应和检验；不显著不等于无效"],
 ["推断边界","六臂/Adam宽区间，floor改变边际","不能改成等价或纯删除因果证据"],
 ["覆盖与部署","覆盖0.750失败单元，真实U未测量","必要范围说明集中一次，失败事实仍可见"]
];
export default function ExperimentNarrativeAudit(){
 const theme=useHostTheme(); const action=useCanvasAction(); const [id,setId]=useState("N5");
 const selected=issues.find(x=>x.id===id)||issues[0]; const open=(path:string)=>action({type:"openFile",path});
 return <Stack gap={24} style={{padding:24,maxWidth:1380,margin:"0 auto",background:theme.bg.editor,color:theme.text.primary}}>
  <Stack gap={8}><Text size="small" tone="secondary">RAVEN-MCS · 实验叙述检查 · 2026-10-17 17:05 PDF</Text><H1>重复否定偏多，需要集中修订叙述</H1><Text weight="semibold" style={{color:theme.accent.primary}}>先讲实验真正支持的认识，再交代必要边界。不能用删除不利事实来改善语气。</Text><Row gap={8} wrap><Button onClick={()=>open(report)}>完整审查</Button><Button variant="secondary" onClick={()=>open(root+"main.pdf")}>当前14页正文</Button></Row></Stack>
  <Grid columns={2} gap={28}><Stack gap={8}><H2>当前判断</H2><Text>City Scanner已提升到正文表II，但泛化的“不证明预测提升”仍分布于摘要、引言、方法、理论、实验和结论。每组结果后的限制语压过了具体认识。</Text></Stack><Stack gap={8}><H2>修改边界</H2><Text>保留不利排序、实际效应、统计结论和因果条件。减少重复总结、主观负面形容和工程核验口吻，不把诊断包装成性能收益。</Text></Stack></Grid>
  <Divider/><Stack gap={12}><H2>八处具体问题与处理方式</H2><Row gap={8} wrap>{issues.map(x=><Pill key={x.id} active={x.id===id} onClick={()=>setId(x.id)}>{x.id}</Pill>)}</Row><Text size="small" tone="secondary">{selected.location+" · "+selected.kind+" · main.tex:"+selected.line}</Text><H2>{selected.problem}</H2><Grid columns={2} gap={24}><Stack gap={8}><Text weight="semibold">必须保留</Text><Text>{selected.keep}</Text></Stack><Stack gap={8}><Text weight="semibold">最小调整</Text><Text>{selected.action}</Text></Stack></Grid><Button variant="secondary" onClick={()=>open(root+"main.tex")}>打开原文</Button></Stack>
  <Stack gap={10}><H2>不可作为“负面措辞”删除的证据</H2><Text size="small" tone="secondary">来源：当前正文第8—13页及相关附录；仅列已知事实类别，不计算情感词频。</Text><Table headers={["对象","必要事实","处理边界"]} rows={protectedFacts} striped/></Stack>
  <Stack gap={8}><H2>应获得解释空间的发现</H2><Text>City Scanner组对齐优势与协议相关的预测取舍；SensorScope投影相对Uniform的0.768 pp；Uniform的收益来源归因；客户端数、权重自由度和可调整目标质量的区别。它们各自支持特定认识。</Text><Text>建议结构：实验问题 → 关键结果与统计依据 → 支持的认识 → 必要的特定边界。全局局限集中归纳，不给否定句设置机械删除配额。</Text></Stack>
  <Divider/><Text size="small" tone="secondary">本轮仅审查，未改论文、未运行实验。对重复与段落结构判断置信度高；未全面重新验证原始实验，不重新评定接收质量。修辞改善不能证明完整P2比简单投影更值得部署。</Text>
 </Stack>;
}
