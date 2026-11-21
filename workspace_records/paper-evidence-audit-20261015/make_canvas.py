from pathlib import Path
import json

out = Path(__file__).parent
data = json.loads((out/'evidence-utilization.json').read_text(encoding='utf-8'))
payload = json.dumps(data, ensure_ascii=False, indent=2)
source = '''import { Stack, Row, Grid, H1, H2, Text, Pill, Table, Button, Divider, useState, useHostTheme, useCanvasAction } from "cursor/canvas";

const evidence = __DATA__;
const categories = ["全部", "未系统纳入", "已写但压缩", "独立或待修复", "已覆盖"];

export default function EvidenceAudit() {
  const theme = useHostTheme();
  const open = useCanvasAction();
  const [category, setCategory] = useState("全部");
  const [selectedId, setSelectedId] = useState("A01");
  const visible = category === "全部" ? evidence : evidence.filter(x => x.coverage === category);
  const selected = visible.find(x => x.id === selectedId) || visible[0];
  const counts = categories.slice(1).map(name => ({ name, count: evidence.filter(x => x.coverage === name).length }));
  const report = "C:/Users/szr/Desktop/record/1/paper-evidence-audit-20261015/UNUSED_AND_UNDERUSED_EXPERIMENTS.md";
  const paper = "C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/";
  const openPath = (path: string) => open({ type: "openFile", path });

  return <Stack gap={20} style={{ padding: 24, color: theme.text.primary, background: theme.bg.editor, maxWidth: 1400, margin: "0 auto" }}>
    <Stack gap={8}>
      <Text size="small" tone="secondary">RAVEN-MCS · 论文与已有实验对照 · 2026-10-15</Text>
      <H1>已有结果，哪些还没有被充分利用？</H1>
      <Text>对照10月12日clean版正文18页与补充材料16页，清点56个results根目录、35个artifacts一级目录，详细评价20组证据。本次只读整理，未训练、回放或修改论文。</Text>
      <Text style={{ color: theme.accent.primary }} weight="semibold">优先整理目标集中度、外生目标、漂移、学习能力与几何诊断；保留负结果和方法身份，不能据此扩大预测收益主张。</Text>
      <Row gap={8} wrap>
        <Button onClick={() => openPath(report)}>打开完整审计报告</Button>
        <Button variant="secondary" onClick={() => openPath(paper + "main.pdf")}>正文</Button>
        <Button variant="secondary" onClick={() => openPath(paper + "supplemental.pdf")}>补充材料</Button>
      </Row>
    </Stack>

    <Grid columns={4} gap={16}>
      {counts.map(x => <Stack key={x.name} gap={4} style={{ borderTop: `1px solid ${theme.stroke.primary}`, paddingTop: 12 }}>
        <H2>{x.count} 组</H2><Text size="small" tone="secondary">{x.name}</Text>
      </Stack>)}
    </Grid>

    <Stack gap={10}>
      <Row gap={8} wrap>{categories.map(name => <Pill key={name} active={category === name} onClick={() => setCategory(name)}>{name}</Pill>)}</Row>
      <Text size="small" tone="secondary">点击实验名称查看完整发现、当前稿位置、利用方式与原始证据。组数是审计条目，不能相加当作独立训练次数。</Text>
      <Table headers={["实验 / 优先级", "当前体现", "已有规模", "已有结果摘要"]}
        rows={visible.map(x => [
          <Stack key={x.id} gap={4}><Button variant="ghost" onClick={() => setSelectedId(x.id)} style={{ height: "auto", textAlign: "left", whiteSpace: "normal", justifyContent: "flex-start" }}>{x.id} · {x.title}</Button><Text size="small" tone="secondary">{x.priority}</Text></Stack>,
          x.coverage,
          <Text key={x.id+"s"} size="small">{x.scale}</Text>,
          <Text key={x.id+"f"} size="small">{x.finding}</Text>
        ])}
        rowTone={visible.map(x => x.id === selected.id ? "info" : "neutral")}
        stickyHeader striped style={{ maxHeight: 620 }} />
    </Stack>

    <Divider />
    <Stack gap={14}>
      <Row gap={10} wrap><Pill>{selected.coverage}</Pill><Text size="small" tone="secondary">{selected.priority}</Text></Row>
      <H2>{selected.id} · {selected.title}</H2>
      <Grid columns="minmax(0, 1.1fr) minmax(0, 1fr)" gap={28}>
        <Stack gap={10}>
          <Text weight="semibold">当前稿如何体现</Text><Text>{selected.paper}</Text>
          <Text weight="semibold">可如何利用</Text><Text>{selected.reuse}</Text>
        </Stack>
        <Stack gap={10} style={{ background: theme.fill.quaternary, padding: 16 }}>
          <Text weight="semibold">引用时必须保留的范围</Text><Text>{selected.limit}</Text>
        </Stack>
      </Grid>
      <Text weight="semibold">已核实存在的证据文件</Text>
      <Row gap={8} wrap>{selected.sources.map(path => <Button key={path} variant="secondary" onClick={() => openPath(path)}>{path.replaceAll("\\\\", "/").split("/").slice(-2).join("/")}</Button>)}</Row>
    </Stack>
    <Divider />
    <Text size="small" tone="secondary">审计依据：完整PDF阅读、TeX结构/表图对照、有限目录清点与选定保存指标。没有逐行重验所有日志或重新认证所有模型。已撤回结果、近似oracle、不同协议及独立OF分支不能拼成统一领先证据。</Text>
  </Stack>;
}
'''.replace('__DATA__', payload)
(out/'experiment-utilization.canvas.tsx').write_text(source,encoding='utf-8')
print('Canvas prepared',len(data),'groups',len(source),'characters')
