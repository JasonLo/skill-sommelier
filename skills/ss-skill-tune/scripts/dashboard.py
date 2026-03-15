#!/usr/bin/env python3
"""
Autoresearch Dashboard — Live visualization of skill optimization progress.

Reads results.jsonl from any autoresearch data directory and serves a
live-updating dashboard.

Usage:
    python3 dashboard.py skills/ss-skill-tune/runs/<name>/data
    python3 dashboard.py skills/ss-skill-tune/runs/<name>/data --port 8501
"""

import argparse
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Autoresearch Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #faf9f7; color: #2d2a26; padding: 32px; max-width: 1200px; margin: 0 auto; }
  .header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
  .header h1 { font-size: 28px; font-weight: 700; }
  .badge { background: #c0392b; color: white; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 4px; letter-spacing: 1px; }
  .subtitle { color: #8a8580; font-size: 14px; margin-top: 4px; }
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
  .stat-card { background: white; border-radius: 12px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .stat-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 8px; }
  .stat-value { font-size: 36px; font-weight: 700; }
  .stat-value.green { color: #27ae60; }
  .stat-value.orange { color: #c0784a; }
  .stat-value.neutral { color: #2d2a26; }
  .chart-container { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 32px; }
  .chart-container canvas { width: 100% !important; height: 300px !important; }
  .criteria-charts { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 32px; }
  .criteria-chart { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .criteria-chart h3 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 12px; }
  .criteria-chart canvas { width: 100% !important; height: 160px !important; }
  .table-container { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 32px; }
  .table-container h3 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; padding: 8px 12px; border-bottom: 1px solid #eee; }
  td { padding: 10px 12px; border-bottom: 1px solid #f5f4f2; font-size: 14px; }
  .status-keep { color: #27ae60; font-weight: 600; }
  .status-discard { color: #8a8580; }
  .prompt-container { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .prompt-container h3 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 12px; }
  .prompt-text { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; line-height: 1.6; color: #4a4540; white-space: pre-wrap; word-break: break-word; background: #faf9f7; padding: 16px; border-radius: 8px; max-height: 400px; overflow-y: auto; }
  @media (max-width: 768px) { .stats { grid-template-columns: repeat(2, 1fr); } .criteria-charts { grid-template-columns: 1fr; } body { padding: 16px; } }
</style>
</head>
<body>
<div class="header">
  <div>
    <div style="display:flex;align-items:center;gap:12px;">
      <h1>Autoresearch</h1>
      <span class="badge">LIVE</span>
    </div>
    <div class="subtitle" id="subtitle">Skill optimization — refreshes every 15s</div>
  </div>
</div>
<div class="stats">
  <div class="stat-card"><div class="stat-label">Current Best</div><div class="stat-value orange" id="stat-best">—</div></div>
  <div class="stat-card"><div class="stat-label">Baseline</div><div class="stat-value neutral" id="stat-baseline">—</div></div>
  <div class="stat-card"><div class="stat-label">Improvement</div><div class="stat-value green" id="stat-improvement">—</div></div>
  <div class="stat-card"><div class="stat-label">Runs / Kept</div><div class="stat-value neutral" id="stat-runs">—</div></div>
</div>
<div class="chart-container"><canvas id="mainChart"></canvas></div>
<div class="criteria-charts" id="criteria-container"></div>
<div class="table-container">
  <h3>Run History</h3>
  <table><thead><tr id="table-header"></tr></thead><tbody id="run-table"></tbody></table>
</div>
<div class="prompt-container">
  <h3>Current Best SKILL.md</h3>
  <div class="prompt-text" id="best-prompt">Loading...</div>
</div>
<script>
const ORANGE='#c0784a',ORANGE_LIGHT='rgba(192,120,74,0.15)',COLORS=['#8e44ad','#2980b9','#27ae60','#d35400','#c0392b','#16a085'];
let mainChart,criteriaCharts={},criteriaNames=[];

function createChart(ctx,label,maxY,color,colorLight){
  return new Chart(ctx,{type:'line',data:{labels:[],datasets:[{label,data:[],borderColor:color,backgroundColor:colorLight,fill:true,tension:0.3,pointRadius:5,pointBackgroundColor:[],pointBorderColor:color,pointBorderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{font:{size:11},color:'#8a8580'}},y:{grid:{color:'#f0efed'},ticks:{font:{size:11},color:'#8a8580'},min:0,max:maxY}}}});
}

function updateChartData(chart,labels,data){
  chart.data.labels=labels;chart.data.datasets[0].data=data;
  let best=-1;chart.data.datasets[0].pointBackgroundColor=data.map(v=>{if(v>best){best=v;return ORANGE}return'#c4c0bb'});
  chart.update('none');
}

async function refresh(){
  let res;try{res=await fetch('/api/data')}catch(e){return}
  const data=await res.json();if(!data.runs||!data.runs.length)return;
  const runs=data.runs,labels=runs.map(r=>r.run),scores=runs.map(r=>r.score),
    baseline=scores[0],best=Math.max(...scores),maxScore=runs[0].max||scores.length;

  document.getElementById('stat-best').textContent=best+'/'+maxScore;
  document.getElementById('stat-baseline').textContent=baseline+'/'+maxScore;
  const imp=baseline>0?((best-baseline)/baseline*100).toFixed(1):'—';
  const el=document.getElementById('stat-improvement');
  el.textContent=imp==='—'?'—':(imp>0?'+':'')+imp+'%';
  el.className='stat-value '+(imp>0?'green':imp<0?'orange':'neutral');

  let kept=0,rb=-1;scores.forEach(s=>{if(s>rb){kept++;rb=s}});
  document.getElementById('stat-runs').textContent=runs.length+' / '+kept;

  // Init charts on first data
  if(!mainChart){mainChart=createChart(document.getElementById('mainChart').getContext('2d'),'Score',maxScore,ORANGE,ORANGE_LIGHT)}
  mainChart.options.scales.y.max=maxScore;
  updateChartData(mainChart,labels,scores);

  // Criteria charts (dynamic)
  const cNames=Object.keys(runs[0].criteria||{});
  if(cNames.join()!==criteriaNames.join()){
    criteriaNames=cNames;
    const container=document.getElementById('criteria-container');container.innerHTML='';criteriaCharts={};
    cNames.forEach((name,i)=>{
      const div=document.createElement('div');div.className='criteria-chart';
      div.innerHTML='<h3>'+name.replace(/_/g,' ')+'</h3><canvas id="c-'+name+'"></canvas>';
      container.appendChild(div);
      const maxC=Math.max(...runs.map(r=>(r.criteria||{})[name]||0),10);
      criteriaCharts[name]=createChart(document.getElementById('c-'+name).getContext('2d'),name,maxC,COLORS[i%COLORS.length],COLORS[i%COLORS.length].replace(')',',0.12)').replace('rgb','rgba'));
    });
  }
  cNames.forEach(name=>{
    const vals=runs.map(r=>(r.criteria||{})[name]||0);
    const maxC=Math.max(...vals,1);
    criteriaCharts[name].options.scales.y.max=maxC;
    updateChartData(criteriaCharts[name],labels,vals);
  });

  // Table
  const hdr=document.getElementById('table-header');
  hdr.innerHTML='<th>Run</th><th>Status</th><th>Score</th>'+cNames.map(n=>'<th>'+n.replace(/_/g,' ')+'</th>').join('')+'<th>Time</th>';
  let rb2=-1;const statuses=scores.map(s=>{if(s>rb2){rb2=s;return'keep'}return'discard'});
  document.getElementById('run-table').innerHTML=runs.map((r,idx)=>{
    const st=statuses[idx],t=r.timestamp?new Date(r.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}):'';
    return'<tr><td>'+r.run+'</td><td class="status-'+st+'">'+st+'</td><td><strong>'+r.score+'/'+r.max+'</strong></td>'+cNames.map(n=>'<td>'+(r.criteria||{})[n]+'</td>').join('')+'<td>'+t+'</td></tr>';
  }).reverse().join('');

  if(data.best_skill)document.getElementById('best-prompt').textContent=data.best_skill;
  document.getElementById('subtitle').textContent='Skill optimization — '+runs.length+' runs';
}
refresh();setInterval(refresh,15000);
</script>
</body>
</html>"""


def make_handler(data_dir: Path):
    results_file = data_dir / "results.jsonl"
    best_skill_file = data_dir / "best_skill.md"

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_TEMPLATE.encode())
            elif parsed.path == "/api/data":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                runs = []
                if results_file.exists():
                    for line in results_file.read_text().strip().split("\n"):
                        if line.strip():
                            try:
                                runs.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                best_skill = ""
                if best_skill_file.exists():
                    best_skill = best_skill_file.read_text().strip()
                self.wfile.write(json.dumps({"runs": runs, "best_skill": best_skill}).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Autoresearch Dashboard")
    parser.add_argument("data_dir", help="Path to autoresearch data directory")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    server = HTTPServer(("0.0.0.0", args.port), make_handler(data_dir))
    print(f"Dashboard running at http://localhost:{args.port}")
    print(f"Reading from: {data_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")


if __name__ == "__main__":
    main()
