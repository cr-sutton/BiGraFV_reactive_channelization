import re, os
D = "/Users/collin/Projects/bipartite_pflotran/src/alpha_study/forsmark_reactive/report_phase1"

def cartoon(name):
    svg = open(f"{D}/cartoons/{name}.svg").read().strip()
    svg = re.sub(r'^<\?xml[^>]*\?>\s*', '', svg)
    cap = open(f"{D}/cartoons/{name}.txt").read().strip()
    return f'<figure>{svg}<figcaption>{cap}</figcaption></figure>'

def sw(base, ext_first, alt, cap, w=1760, h=990):
    return (f'<figure><img src="img/{base}{ext_first}.png" data-axbase="img/{base}" alt="{alt}" loading="lazy">'
            f'<figcaption>{cap}</figcaption></figure>')

def fig(src, alt, cap, style=""):
    st = f' style="{style}"' if style else ""
    return f'<figure><img src="img/{src}" alt="{alt}" loading="lazy"{st}><figcaption>{cap}</figcaption></figure>'

AXBAR = '''<div class="axbar" role="group" aria-label="Time axis for the figures">
<span>Time axis (all switchable figures)</span>
<button type="button" data-ax="tcap" aria-pressed="true">capacity time t<sub>cap</sub></button>
<button type="button" data-ax="pv" aria-pressed="false">pore volumes PV</button>
<button type="button" data-ax="tauH" aria-pressed="false">dissolved volume / initial volume &tau;</button>
</div>'''

CSS = r'''
:root{--bg:#f7f7f4;--surface:#fff;--ink:#16181a;--ink-2:#4c5157;--rule:#dcdcd6;--accent:#1f5f8b;--hl:#eaf2f8;
--mineral:#8a8f96;--open:#9fd3f0;--calcite:#e9b949;--flow:#d2572a;--ion:#6b4fbb;--rock:#d9d4c7;
--font-display:"Newsreader",Georgia,"Times New Roman",serif;--font-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--font-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15171a;--surface:#1d2024;--ink:#ebebe6;--ink-2:#b2b6ba;--rule:#34383d;--accent:#7db4dc;--hl:#1f2a33;
--mineral:#5d636b;--open:#3d8fc0;--calcite:#c9982e;--flow:#f08a5d;--ion:#a48ae8;--rock:#4a463e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15171a;--surface:#1d2024;--ink:#ebebe6;--ink-2:#b2b6ba;--rule:#34383d;--accent:#7db4dc;--hl:#1f2a33;
--mineral:#5d636b;--open:#3d8fc0;--calcite:#c9982e;--flow:#f08a5d;--ion:#a48ae8;--rock:#4a463e;color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--font-body);overflow-x:hidden}
main{max-width:1080px;margin:0 auto;padding:40px 20px 80px}
.col{max-width:70ch}
h1,h2,h3{font-family:var(--font-display);font-weight:600;line-height:1.2;text-wrap:balance;margin:0}
h1{font-size:2.5rem}
h2{font-size:1.6rem;margin-top:48px;padding-top:16px;border-top:1px solid var(--rule)}
h3{font-size:1.15rem;margin-top:24px}
p,ul,ol{margin:8px 0}li{margin:4px 0}
.meta{color:var(--ink-2);font-size:.92rem}
.lede{font-size:1.1rem}
.summary{background:var(--hl);border-left:4px solid var(--accent);border-radius:0 6px 6px 0;padding:10px 16px;margin:12px 0;max-width:70ch}
.summary p{margin:4px 0}
.summary .tag{font-family:var(--font-mono);font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;color:var(--accent)}
.eq{margin:10px 0;overflow-x:auto;overflow-y:hidden;max-width:100%}
mjx-container[display="true"]{margin:.6em 0 !important}
.where{color:var(--ink-2);font-size:.92rem;margin-top:0;max-width:70ch}
.status{display:inline-block;font-family:var(--font-mono);font-size:.74rem;padding:1px 8px;border-radius:999px;border:1px solid var(--rule);background:var(--surface);color:var(--ink-2);margin-left:6px;vertical-align:1px}
.status.pub{border-color:var(--accent);color:var(--accent)}
.status.ours{border-color:var(--flow);color:var(--flow)}
.item{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:4px 16px 8px;margin:14px 0;max-width:72ch}
.item h3{margin-top:10px}
figure{margin:16px 0;background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:12px}
figure img{display:block;max-width:100%;height:auto;margin:0 auto;background:#fff;border-radius:3px}
figcaption{color:var(--ink-2);font-size:.9rem;margin-top:8px;max-width:90ch}
svg.cartoon{width:100%;height:auto;display:block;color:var(--ink)}
video{width:100%;height:auto;display:block;border-radius:3px;background:#fff}
.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.tablewrap{overflow-x:auto;margin:12px 0;background:var(--surface);border:1px solid var(--rule);border-radius:6px;max-width:100%}
table{border-collapse:collapse;width:100%;font-size:.9rem;font-variant-numeric:tabular-nums}
th,td{padding:6px 12px;text-align:right;border-bottom:1px solid var(--rule);white-space:nowrap}
th{font-weight:600;color:var(--ink-2);font-size:.8rem}
th:first-child,td:first-child,th.l,td.l{text-align:left}
td.wrap{white-space:normal;min-width:16rem}
tr:last-child td{border-bottom:0}
.src{color:var(--ink-2);font-size:.84rem;margin:-6px 0 10px}
code,.mono{font-family:var(--font-mono);font-size:.86em}
.note{border-left:3px solid var(--accent);padding:4px 14px;margin:14px 0;background:var(--surface);max-width:70ch}
.warn{border-left:3px solid var(--flow);padding:4px 14px;margin:14px 0;background:var(--surface);max-width:70ch}
.pending{border:1px dashed var(--rule);border-radius:6px;padding:8px 14px;color:var(--ink-2);background:var(--surface);max-width:70ch}
.claim{font-weight:600}
.axbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:14px 0 4px;font-size:.9rem}
.axbar span{color:var(--ink-2);margin-right:4px}
.axbar button{font:inherit;font-size:.86rem;padding:5px 12px;border-radius:999px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);cursor:pointer}
.axbar button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.axbar button:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
a{color:var(--accent);overflow-wrap:anywhere}
ol.refs{padding-left:1.6rem;font-size:.9rem}
ol.refs li{margin:6px 0}
nav.toc{font-size:.9rem;display:flex;flex-wrap:wrap;gap:4px 14px;margin:12px 0}
@media (max-width:420px){h1{font-size:1.9rem}main{padding:24px 16px 60px}}
'''

JS = '''(function(){
function setAxis(ax){
document.querySelectorAll("img[data-axbase]").forEach(function(im){im.src=im.dataset.axbase+ax+".png";});
document.querySelectorAll(".axbar button").forEach(function(b){b.setAttribute("aria-pressed",String(b.dataset.ax===ax));});
try{localStorage.setItem("forsmark-axis",ax);}catch(e){}
}
document.querySelectorAll(".axbar button").forEach(function(b){b.addEventListener("click",function(){setAxis(b.dataset.ax);});});
try{var s=localStorage.getItem("forsmark-axis");if(s)setAxis(s);}catch(e){}
})();'''

def S(txt):  # summary box
    return f'<div class="summary"><span class="tag">In plain words</span>{txt}</div>'

body = []
A = body.append

# ---------- 1 header
A(f'''<header class="col">
<p class="meta">BiGraFV reactive study &middot; Forsmark FFM01 &middot; 3 November 2026 &middot; Phase 1 complete, Phase 2 running</p>
<h1>Forsmark Reactive Channels</h1>
<p class="lede">How do dissolution channels form in a kilometre-scale, mineral-filled fracture network, and how does calcite precipitation change them? This page reports 90 Phase 1 runs and the first Phase 2 tests.</p>
<nav class="toc" aria-label="Sections"><a href="#brief">In brief</a><a href="#setup">What we simulated</a><a href="#clocks">Three clocks</a><a href="#measures">Measures</a><a href="#results">Results</a><a href="#candidates">Candidate findings</a><a href="#new">New or not</a><a href="#limits">Limits and decisions</a><a href="#refs">References</a><a href="#appendix">Appendix</a></nav>
</header>
<section id="brief">
<h2>1. In brief</h2>
{S("<p>We dissolved gypsum, alone and coupled to calcite precipitation, in 45 networks of 1,587 to 8,229 fractures. The flow concentrates into a few paths that already existed, then spreads again. The results below are the evidence for that, plus five candidate findings that need more tests.</p>")}
<div class="col"><ul>
<li><strong>What we did.</strong> 90 reactive runs on 45 networks built from SKB Forsmark FFM01 fracture statistics (1000 &times; 250 &times; 250 m), with one network pore volume injected per year. The solver is BiGraFV (one control volume per fracture) in PFLOTRAN.</li>
<li><strong>Four stages.</strong> (1) Pore space opens near the inlet while flow is still spread over filled fractures. (2) A front advances down the paths that already carried the most flow. (3) It breaks through at the outlet. (4) Neighbouring paths open and the flow spreads out again.</li>
<li><strong>Channel depth (early Phase 2).</strong> How strongly flow focuses depends on the permeability gain a dissolved fracture can reach, not on the chemistry. Equal ceilings (&times;10 to &times;10.6) gave equal depth within about 0.01. Three seeds so far.</li>
<li><strong>Transport narrows.</strong> While the channel forms, tracer arrives closer to the mean residence time and the breakthrough tail steepens. Both recover after the channel dissolves through. Coarse probes; finer ones are being added.</li>
<li><strong>A compact front.</strong> Breakthrough over 1 km needs 53&ndash;57 % (gypsum-only) or 58&ndash;67 % (coupled) of the gypsum dissolved (medians), not a few percent. This is a result of the one-cell model and is stated with its caveats in section 6.</li>
<li><strong>What is not new.</strong> Channels following the initial network structure, and replacement by calcite limiting the permeability gain, are known (Hyman et al. 2026; Szawe&#322;&#322;o et al. 2026; Budek et al. 2026). We show them at 1 km.</li>
</ul></div>
<p class="pending">Status. Phase 2 (mechanism tests) and the P32 &times;16 network set are still running. This page is updated as they finish.</p>
</section>''')

# ---------- 2 setup
A(f'''<section id="setup">
<h2>2. What we simulated</h2>
{S("<p>Each fracture in a synthetic Forsmark network is one well-mixed cell that starts 90 % full of gypsum. Water is pumped through at a fixed rate. The cell dissolves gypsum, and in the coupled case calcite grows back. Permeability follows the open pore space.</p>")}
<h3>Networks</h3>
<div class="col"><ul>
<li>Domain 1000 &times; 250 &times; 250 m. Flow runs along x, inlet at x = &minus;500 m, outlet at x = +500 m.</li>
<li>Geometry: SKB FFM01 open-fracture sets NS, NE, NW, EW, HZ for 200&ndash;400 m depth (SKB 2010, Table 6-75): Fisher &kappa; 12.9&ndash;17.8, truncated power-law radii with k<sub>r</sub> 2.38&ndash;3.10, radii 15&ndash;564 m. Generated by <code>network_forsmark.py</code> and dfnWorks (Hyman et al. 2015).</li>
<li>At the real SKB intensity nothing percolates across 1 km, so fracture intensity P32 is scaled by &times;4, &times;6, &times;8 (and &times;16, running).</li>
<li>Transmissivity \\(T = 6.3\\times10^{{-9}}\\,r^{{1.3}}\\) m&sup2;/s with a semi-correlated spread &sigma; = 0, 0.5, 1.0 (the SKB fit is 1.0). dfnWorks converts T to aperture with the cubic law. For one seed and P32, the three &sigma; share identical geometry. &sigma; is always shown as separate ensembles.</li>
<li>5 seeds per (P32, &sigma;): 45 networks; &times;16 adds 15.</li>
</ul></div>
<div class="warn"><strong>Transmissivity depth caveat.</strong> The fracture intensities are SKB&rsquo;s values for 200&ndash;400 m depth. The law \\(T=6.3\\times10^{{-9}}r^{{1.3}}\\), &sigma; = 1.0 is SKB&rsquo;s transmissivity model for depths <em>above</em> 200 m. For 200&ndash;400 m the table gives a semi-correlated law \\(1.3\\times10^{{-9}}r^{{0.5}}\\) (&sigma; = 1.0) and a correlated law \\(1.6\\times10^{{-9}}r^{{0.8}}\\). At r = 100 m our law gives 2.5&times;10<sup>&minus;6</sup> m&sup2;/s and the 200&ndash;400 m semi-correlated law 1.3&times;10<sup>&minus;8</sup> m&sup2;/s, about 190 times lower. Our &sigma; = 0 case also uses the semi-correlated exponent pair, not the table&rsquo;s correlated pair. With a fixed flow rate the absolute T does not matter, but the contrast between large and small fractures does. We therefore label the networks &ldquo;FFM01 200&ndash;400 m geometry with the FFM01 0&ndash;200 m transmissivity model&rdquo;. See the decision in section 8.</div>
<div class="tablewrap"><table>
<thead><tr><th class="l">P32 scale</th><th>fractures</th><th>fracture-disjoint inlet&ndash;outlet paths</th></tr></thead>
<tbody><tr><td>&times;4</td><td>1,587&ndash;1,814</td><td>9&ndash;12</td></tr>
<tr><td>&times;6</td><td>2,714&ndash;3,037</td><td>22&ndash;27</td></tr>
<tr><td>&times;8</td><td>3,812&ndash;4,070</td><td>38&ndash;44</td></tr>
<tr><td>&times;16 (running)</td><td>7,849&ndash;8,229</td><td>114&ndash;141 (78k graph cells)</td></tr></tbody></table></div>
<p class="src">Source: forsmark_reactive/phase1/network_stats.json.</p>

<h3>BiGraFV: one cell per fracture</h3>
<div class="col"><p>BiGraFV is a bipartite-graph finite-volume model (unpublished; this work). Each fracture is one control volume. Fracture intersections are the connections. PFLOTRAN solves flow and reactive transport on the resulting graph. A fracture is well mixed along its whole length, so the model has no in-plane fronts or wormholes. Dead-end fractures are represented only approximately. We use the plain one-cell model, real mineral rate constants, a fixed volumetric flow, and no dead-end explanations.</p></div>
{cartoon("fracture_cell")}

<h3>Chemistry</h3>
<div class="col"><p>Gypsum dissolves and calcite precipitates:</p></div>
\\[ \\mathrm{{CaSO_4\\cdot 2H_2O \;\\rightleftharpoons\; Ca^{{2+}} + SO_4^{{2-}} + 2H_2O}} \\]
\\[ \\mathrm{{Ca^{{2+}} + CO_3^{{2-}} \;\\rightleftharpoons\; CaCO_3}} \\]
<div class="col"><p>Each reaction follows a transition-state-theory (TST) rate law (Hyman et al. 2024a, Eq. A.4; Lichtner et al. 2015):</p></div>
\\[ r_m = -A_m\\,k_m\\left(1-\\frac{{Q_m}}{{K_m}}\\right) \\]
<p class="where">\\(r_m\\): net reaction rate of mineral \\(m\\) (negative = dissolution; \\(Q_m/K_m&lt;1\\) gives dissolution). \\(A_m\\): reactive surface area of mineral \\(m\\). \\(k_m\\): rate constant (mol m<sup>&minus;2</sup> s<sup>&minus;1</sup>). \\(Q_m\\): ion activity product. \\(K_m\\): equilibrium constant. PFLOTRAN writes the same law with the inverse ratio and the opposite sign (Lichtner et al. 2015).</p>
<div class="col"><ul>
<li>Rate constants lie inside the range of Hyman et al. (2024a) Table 1: k<sub>gyp</sub> = 1.62&times;10<sup>&minus;3</sup> mol m<sup>&minus;2</sup> s<sup>&minus;1</sup> (the top of that range) and k<sub>cal</sub> = 2.29&times;10<sup>&minus;5</sup>. Gypsum specific surface 750 m&sup2;/kg (inside the paper&rsquo;s 486&ndash;4670 range); calcite area 200 m&sup2;/m&sup3;.</li>
<li>Gypsum-only runs inject dilute water. Coupled runs inject the paper&rsquo;s Table 2 brine: 0.5 M CO<sub>3</sub>, 1.0 M Na, pH 11.39.</li>
</ul></div>
{cartoon("chemistry")}
<h3>Permeability law and ceilings</h3>
<div class="col"><p>Porosity is \\(\\phi = 1-\\sum_m \\phi_m\\), where \\(\\phi_m\\) is the volume fraction of mineral \\(m\\). Permeability follows the PFLOTRAN power law (Lichtner et al. 2015; Hyman et al. 2024b):</p></div>
\\[ \\frac{{k}}{{k_0}}=\\left(\\frac{{\\phi-\\phi_c}}{{\\phi_0-\\phi_c}}\\right)^{{n}},\\qquad \\phi_c=0,\; n=1 \;\\Rightarrow\; \\frac{{k}}{{k_0}}=\\frac{{\\phi}}{{\\phi_0}} \\]
<p class="where">\\(k_0\\), \\(\\phi_0\\): initial permeability and porosity (\\(\\phi_0=0.1\\); the reference is the material porosity). \\(\\phi_c\\): critical porosity (0 here). \\(n\\): exponent (1 here).</p>
<div class="col"><p>Because the cell has fixed walls, permeability can rise only until the vein is gone. For gypsum-only runs this ceiling is \\(1/\\phi_0\\). With calcite replacing gypsum, the ceiling depends on the replacement ratio \\(\\Gamma\\) (Budek et al. 2026, Eq. 9):</p></div>
\\[ \\Gamma=\\frac{{V_\\mathrm{{cal}}}}{{V_\\mathrm{{gyp}}}}=\\frac{{36.934}}{{74.69}}=0.494,\\qquad \\left.\\frac{{k}}{{k_0}}\\right|_\\mathrm{{max}}=1+\\frac{{v_{{f0}}}}{{\\phi_0}}\\,(1-\\Gamma) \\]
<p class="where">\\(V_\\mathrm{{gyp}}\\), \\(V_\\mathrm{{cal}}\\): molar volumes of gypsum and calcite (cm&sup3;/mol). \\(v_{{f0}}\\): initial gypsum volume fraction (0.9 at \\(\\phi_0=0.1\\)). The coupled ceiling is our derivation; it assumes all dissolved calcium re-precipitates in place as calcite. Budek et al. (2026) state that \\(\\Gamma&lt;1\\) lets porosity reopen.</p>
<div class="tablewrap"><table>
<thead><tr><th class="l">Ceiling</th><th>&phi;<sub>0</sub> = 0.1</th><th>&phi;<sub>0</sub> = 0.05</th></tr></thead>
<tbody><tr><td>gypsum-only</td><td>&times;10</td><td>&times;20</td></tr>
<tr><td>coupled</td><td>&times;5.5</td><td>&times;10.6</td></tr></tbody></table></div>
<h3>Flow rate</h3>
<div class="col"><p>Flow is fixed: one network pore volume per year. On these networks this equals a head gradient of about 10<sup>&minus;4</sup> to 10<sup>&minus;3</sup> across 1 km, inside the natural groundwater range. The convention comes from Hyman et al. (2024b), who write &ldquo;the initial volume of each fracture network per year&rdquo;. That text does not say whether &ldquo;volume&rdquo; means bulk fracture volume or pore volume. We use pore volume. If they meant bulk volume, our rate is 0.1 of theirs per unit bulk volume (&times;1 &minus; v<sub>f0</sub>).</p>
<p>Outlet boundary fix. The graph-to-PFLOTRAN writer gave 1000 m&sup2; outflow faces. We rescale them to 0.01 &times; distance (<code>exfix_outflow.py</code>). A control run agreed within 8&times;10<sup>&minus;4</sup> in dissolved fraction and 0.25 % in k<sub>eff</sub>, so the 60 earlier runs stand.</p></div>
<div class="tablewrap"><table>
<thead><tr><th class="l">Parameter</th><th class="l">Value</th></tr></thead>
<tbody>
<tr><td class="l">Domain</td><td class="l">1000 &times; 250 &times; 250 m, flow along x</td></tr>
<tr><td class="l">P32 scale</td><td class="l">&times;4, &times;6, &times;8 (&times;16 running) of SKB value</td></tr>
<tr><td class="l">Transmissivity</td><td class="l">T = 6.3&times;10<sup>&minus;9</sup> r<sup>1.3</sup> m&sup2;/s; &sigma; = 0, 0.5, 1.0</td></tr>
<tr><td class="l">Seeds / networks</td><td class="l">5 per (P32, &sigma;); 45 networks (+15 at &times;16)</td></tr>
<tr><td class="l">Initial state</td><td class="l">90 % gypsum by volume, &phi;<sub>0</sub> = 0.1; k/k<sub>0</sub> = &phi;/&phi;<sub>0</sub></td></tr>
<tr><td class="l">k<sub>gyp</sub>, k<sub>cal</sub></td><td class="l">1.62&times;10<sup>&minus;3</sup>, 2.29&times;10<sup>&minus;5</sup> mol m<sup>&minus;2</sup> s<sup>&minus;1</sup></td></tr>
<tr><td class="l">Surface area</td><td class="l">gypsum 750 m&sup2;/kg; calcite 200 m&sup2;/m&sup3;</td></tr>
<tr><td class="l">Injected water</td><td class="l">gypsum-only: dilute; coupled: 0.5 M CO<sub>3</sub>, 1.0 M Na, pH 11.39</td></tr>
<tr><td class="l">Flow</td><td class="l">1 network pore volume per year, fixed</td></tr>
<tr><td class="l">Phase 1 run length</td><td class="l">36,515 PV</td></tr>
</tbody></table></div>
<p class="src">Source: BRIEF.md (3 Nov 2026), Hyman et al. 2024a Tables 1&ndash;2.</p>
</section>''')

# ---------- 3 clocks
A(f'''<section id="clocks">
<h2>3. How we measure time (three clocks)</h2>
{S("<p>The two chemistries run at very different speeds per pore volume, so a single clock hides what they share. We use three clocks: pore volumes injected, a capacity-normalised time that puts both chemistries on one scale, and the dissolved volume as a fraction of the initial pore volume. Every time-dependent figure below can be switched between the three.</p>")}
<div class="item"><h3>Clock 1: pore volumes injected <span class="status pub">published convention</span></h3>
\\[ \\mathrm{{PV}}=\\frac{{Q\\,t}}{{V_{{p0}}}} \\]
<p class="where">\\(Q\\): fixed volumetric flow rate (m&sup3;/yr). \\(t\\): time (yr). \\(V_{{p0}}\\): initial pore volume of the network (m&sup3;). At one pore volume per year, PV equals t in years.</p>
<p>Meaning: how many network pore volumes of water have passed through. Backing: injected volume over a reference volume is the standard clock (Szymczak &amp; Ladd 2009, Fig. 16), and the fixed-rate convention is from Hyman et al. (2024b). The pore-volume reading of that convention is our choice.</p></div>
<div class="item"><h3>Clock 2: capacity-normalised time <span class="status ours">our construction</span></h3>
\\[ t_\\mathrm{{cap}}=\\mathrm{{PV}}\;\\frac{{c_\\mathrm{{cap}}}}{{C_\\mathrm{{inv}}}},\\qquad C_\\mathrm{{inv}}=\\frac{{v_{{f0}}}}{{(1-v_{{f0}})\\,V_\\mathrm{{gyp}}}} \\]
<p class="where">\\(c_\\mathrm{{cap}}\\): gypsum (mol) that 1 m&sup3; of injected water can remove if it leaves saturated. It is 16.6 mol/m&sup3; for dilute water (gypsum solubility) and \\(16.6+1000\\,[\\mathrm{{CO_3}}]\\) mol/m&sup3; for the brine, with \\([\\mathrm{{CO_3}}]\\) in mol/L (one Ca removed as calcite per CO<sub>3</sub>; 516.6 for 0.5 M). \\(C_\\mathrm{{inv}}\\): gypsum inventory per m&sup3; of pore, 120,498 mol/m&sup3; (\\(v_{{f0}}=0.9\\), \\(V_\\mathrm{{gyp}}=74.69\\) cm&sup3;/mol).</p>
<p>Meaning: \\(t_\\mathrm{{cap}}=1\\) is the point where the injected water could have dissolved the whole inventory. At high Damk&ouml;hler number the dissolved fraction is about \\(t_\\mathrm{{cap}}\\) (within about 0.01 at the channel minimum).</p>
<p><strong>Backing.</strong> This is our normalisation, not a published quantity. The closest published form is Szymczak &amp; Ladd (2009, Eq. 52): the volume of reactive fluid needed to dissolve a solid volume equal to the initial pore space. Our \\(t_\\mathrm{{cap}}\\) equals their \\(V_\\mathrm{{inj}}/V_0\\) divided by 9 at \\(v_{{f0}}=0.9\\), because we count the whole solid inventory (9 times the pore volume). The capacity idea itself is the acid capacity number \\(\\gamma=c_0/(\\nu c_\\mathrm{{sol}})\\), &ldquo;how much solid a unit volume of reactant can dissolve&rdquo; (Hyman et al. 2026, p. 6; Szymczak &amp; Ladd 2012). For dilute gypsum \\(c_\\mathrm{{cap}}V_\\mathrm{{gyp}}=16.6\\times74.69\\times10^{{-6}}=1.24\\times10^{{-3}}\\), the analogue of \\(\\gamma\\). The &ldquo;pore volumes to dissolve&rdquo; idea is also used in acidizing (Fredd &amp; Fogler 1998; read only through secondary sources).</p>
<p><strong>Caveat.</strong> \\(c_\\mathrm{{cap}}\\) is an upper bound because it assumes water leaves saturated. For the brine the ideal value is 516.6 mol/m&sup3; and the pilot measured about 470 mol/m&sup3; (about 9 % lower). Coupled curves therefore sit slightly to the right of the ideal.</p></div>
<div class="item"><h3>Clock 3: dissolved volume over initial volume <span class="status pub">published, extended</span></h3>
\\[ \\tau=\\frac{{\\Delta V}}{{V_0}},\\qquad \\Delta V=n_\\mathrm{{gyp,diss}}\\,V_\\mathrm{{gyp}}-n_\\mathrm{{cal,form}}\\,V_\\mathrm{{cal}} \\]
<p class="where">\\(\\Delta V\\): net open volume gained (m&sup3;). \\(n_\\mathrm{{gyp,diss}}\\): moles of gypsum dissolved. \\(n_\\mathrm{{cal,form}}\\): moles of calcite formed. \\(V_\\mathrm{{cal}}=36.934\\) cm&sup3;/mol. \\(V_0\\): initial pore volume.</p>
<p>Meaning: how much new open volume the reaction has made, in units of the starting open volume. Backing: Hyman et al. (2026, Eq. 26) define \\(\\tau=\\Delta V_\\mathrm{{tot}}/V_0\\) for dissolution only, with \\(\\tau\\le1\\). Our use is an extension: it runs past 1 (to about 9 for gypsum-only and about 4.5 for coupled, because the fractures start 90 % filled), and it subtracts calcite. \\(\\tau=1\\) arrives at \\(t_\\mathrm{{cap}}=0.11\\) for gypsum-only.</p></div>
{cartoon("capacity_clock")}
<h3>How the figure switch works</h3>
<div class="col"><p>Use the three buttons above any switchable figure. All switchable figures on the page change together and the choice is remembered. Capacity time is the default because it overlays the two chemistries. Pore volumes show the real injected amount. &tau; shows the open volume gained.</p></div>
</section>''')

# ---------- 4 measures
A(f'''<section id="measures">
<h2>4. How we measure channels and transport</h2>
{S("<p>Channels are measured by how unevenly the flow is shared among fractures, in several ways that answer different questions. Transport is measured by pushing a tracer pulse through a frozen snapshot of the permeability field and reading its arrival curve. Each measure is defined once here.</p>")}
<div class="item"><h3>Volume-weighted participation ratio <span class="status ours">our extension</span></h3>
\\[ \\mathrm{{PR}}_V=\\frac{{\\left(\\sum_f Q_f\\right)^2}}{{\\sum_f Q_f^2/w_f}},\\qquad w_f=\\frac{{V_f}}{{\\sum_f V_f}} \\]
<p class="where">\\(Q_f\\): flow through fracture \\(f\\) (m&sup3;/s). \\(V_f\\): its fracture volume. \\(w_f\\): its share of the total fracture volume. \\(\\mathrm{{PR}}_V=1\\) when flow is proportional to volume; it is small when a few fractures carry most of the flow relative to their volume.</p>
<p>Backing: it is the weighted form of the participation ratio of Bell et al. (1970) and Edwards &amp; Thouless (1972), as used for flow localisation by Maillot et al. (2016) and Hyman (2020). The volume weighting is ours. If one fracture carries all flow, \\(\\mathrm{{PR}}_V=w_f\\).</p></div>
<div class="item"><h3>Pore-volume participation ratio <span class="status ours">our extension</span></h3>
<p>\\(\\mathrm{{PR}}_\\mathrm{{pore}}\\) is the same expression with \\(w_f=V_f\\phi_f/\\sum_f V_f\\phi_f\\), the share of the <em>open</em> pore volume. \\(\\phi_f\\) is the porosity of fracture \\(f\\). It asks how the flow compares with where the open space is.</p></div>
<div class="item"><h3>Active surface area \\(d_Q\\) <span class="status pub">published</span></h3>
\\[ d_Q=\\frac{{1}}{{V}}\\,\\frac{{\\left(\\sum_f S_f\\,Q_f\\right)^2}}{{\\sum_f S_f\\,Q_f^{{2}}}},\\qquad \\text{{reported as }}100\\,d_Q/P_{{32}} \\]
<p class="where">\\(S_f\\): area of fracture \\(f\\) (m&sup2;). \\(Q_f\\): half the absolute total volumetric flow the fracture exchanges with its neighbours. \\(V\\): domain volume. \\(P_{{32}}\\): fracture area per unit volume.</p>
<p>Meaning: the share of fracture surface where flow is significant. Source: Maillot et al. (2016, Eq. 8), reproduced in Hyman (2020), Hyman et al. (2024b) and Hyman et al. (2026). An earlier version of this page used a flux-density form; it was wrong and is replaced by this form.</p></div>
<div class="item"><h3>n90 and inheritance <span class="status ours">our definitions</span></h3>
<p>\\(n_{{90}}\\): number of fractures that carry 90 % of the throughflow. Let \\(S_t\\) be that set at time \\(t\\).</p>
\\[ \\text{{inheritance}}(t)=\\frac{{|S_t\\cap S_0|}}{{|S_t|}},\\qquad J(A,B)=\\frac{{|A\\cap B|}}{{|A\\cup B|}} \\]
<p class="where">\\(S_0\\): the initial 90 %-flow set. Inheritance is the share of the current set that was already in the initial set (called overlap0 in the code). \\(J\\): Jaccard overlap, used to compare the sets chosen by the two chemistries.</p></div>
<div class="item"><h3>Outlet dissolution and breakthrough <span class="status ours">our definition</span></h3>
<p>Outlet dissolution is the flow-weighted dissolved fraction of the fractures whose centres lie in the last 100 m (x &gt; 400 m). Breakthrough is the first saved state where it reaches 0.5. The &ldquo;leading edge&rdquo; in the maps is the position where flow paths are at least 50 % dissolved, averaged over 100 m.</p></div>
<div class="item"><h3>Breakthrough curve and its percentiles <span class="status pub">adapted</span></h3>
\\[ F(t)=\\int_0^t f(s)\\,\\mathrm{{d}}s,\\qquad F(t_{{16}})=0.16,\; F(t_{{50}})=0.50,\; F(t_{{84}})=0.84 \\]
<p class="where">\\(f(t)\\): outflow tracer flux divided by the injected tracer amount (1/yr), the breakthrough curve. \\(F\\): its cumulative. \\(t_{{16}},t_{{50}},t_{{84}}\\): arrival times at those percentiles.</p>
<p>Definitions follow Hyman et al. (2024b, Eq. 18; 2026, Eqs. 30&ndash;33). They use particle tracking. We inject an Eulerian pulse into a frozen flow and permeability field (numerical dispersion smears the first arrival), so this is our adaptation. The flux-weighted versus resident-injection distinction is in Kreft &amp; Zuber (1978).</p></div>
<div class="item"><h3>Longitudinal dispersion and dispersivity <span class="status pub">published form</span></h3>
\\[ D_L=\\frac{{1}}{{8}}\\left[\\frac{{L-v\\,t_{{16}}}}{{\\sqrt{{t_{{16}}}}}}-\\frac{{L-v\\,t_{{84}}}}{{\\sqrt{{t_{{84}}}}}}\\right]^2,\\qquad v=\\frac{{L}}{{t_{{50}}}},\\qquad \\alpha_L=\\frac{{D_L}}{{v}} \\]
<p class="where">\\(L=1000\\) m: transport distance. \\(v\\): median velocity (m/yr). \\(D_L\\): effective longitudinal dispersion (m&sup2;/yr). \\(\\alpha_L\\): dispersivity (m).</p>
<p>Source: Hyman et al. (2026, Eq. B1), after Sahimi (2011). It follows from the 1-D advection-dispersion solution, where a Gaussian arrival has \\((L-vt)/\\sqrt{{2D t}}=\\pm1\\) at the 16th and 84th percentiles. \\(\\alpha_L=D_L/v\\) is our addition.</p></div>
<div class="item"><h3>Tail exponent and residence-time normalisation <span class="status ours">our choices</span></h3>
\\[ f(t)\\propto t^{{-\\gamma}},\\qquad \\tau_\\mathrm{{res}}=\\frac{{V_p}}{{Q}} \\]
<p class="where">\\(\\gamma\\): tail exponent, from a least-squares line in log-log coordinates over \\(t\\in[2\\,t_\\mathrm{{peak}},\\,t \\text{{ where }} f=10^{{-2}}f_\\mathrm{{peak}}]\\). \\(\\tau_\\mathrm{{res}}\\): current mean residence time. \\(V_p\\): current pore volume (m&sup3;).</p>
<p>Hyman et al. (2026, Eq. 34) define the power-law tail and fit in log-log space, but do not give a fit window; the window above is ours. They normalise times by the first arrival of the unreacted network. We also divide arrivals by \\(\\tau_\\mathrm{{res}}\\), because the probes hold \\(Q\\) fixed while the pore volume grows up to &times;10.</p></div>
</section>''')

# ---------- 5 results
A(f'''<section id="results">
<h2>5. Results</h2>
{S("<p>All 90 Phase 1 runs finished. Both chemistries make a temporary channel, then spread out. The coupled brine is about 30 times faster per pore volume, but the two share one clock once time is scaled by capacity. All numbers are medians unless stated.</p>")}
<h3>5a. Chemistry and capacity</h3>
<div class="col"><p>Dilute water leaves carrying about 17 mol/m&sup3;. The 0.5 M brine leaves carrying about 470&ndash;500 mol/m&sup3;. So the coupled runs dissolve about 30 times faster per pore volume. On capacity time the two chemistries share a clock. No coupled run clogged.</p></div>
<div class="tablewrap"><table>
<thead><tr><th class="l">Chemistry</th><th>P32 &times;4</th><th>&times;6</th><th>&times;8</th></tr></thead>
<tbody>
<tr><td class="l">gypsum dissolved at 36,515 PV, gypsum-only</td><td>0.896</td><td>0.936</td><td>0.970</td></tr>
<tr><td class="l">gypsum dissolved at 36,515 PV, coupled</td><td>0.937</td><td>0.976</td><td>0.990</td></tr>
</tbody></table></div>
<p class="src">Source: forsmark_reactive/phase1/phase1_end_summary.csv. The k<sub>eff</sub> gain at the end is 9.90&ndash;9.97 for gypsum-only and 5.35&ndash;5.41 for coupled, across P32.</p>
{fig("phase1_dissolved.png","Fraction of gypsum dissolved against pore volumes injected for P32 x4, x6, x8, both chemistries.","Gypsum dissolved against pore volumes (median with 10&ndash;90 % band). Look at the horizontal gap between the coupled and gypsum-only curves: it is the factor of about 30. Both level off below 1.")}
{fig("phase1_keff.png","Effective permeability gain against pore volumes injected.","Effective permeability relative to the start. Look at the plateaus: about 5.4 for coupled (the &times;5.5 ceiling) and about 9.9 for gypsum-only (the &times;10 ceiling).")}
<h3>5b. Density: active area falls, participation rises</h3>
<div class="col"><p>As P32 rises, the active-surface measure \\(100\\,d_Q/P_{{32}}\\) falls while \\(\\mathrm{{PR}}_V\\) rises. Both are real and measure different things. Denser networks carry flow more in proportion to fracture volume (\\(\\mathrm{{PR}}_V\\) up). A smaller share of the fracture surface carries significant flow, because most added fractures are small and nearly idle (\\(d_Q\\) down). The share of fractures, by count, that carry flow falls from 0.041 to 0.034.</p></div>
<div class="tablewrap"><table>
<thead><tr><th class="l">At the start (median)</th><th>P32 &times;4</th><th>&times;6</th><th>&times;8</th></tr></thead>
<tbody>
<tr><td class="l">100 d<sub>Q</sub>/P32 (%)</td><td>about 22.5</td><td>about 17.5</td><td>about 15.0</td></tr>
<tr><td class="l">PR<sub>V</sub></td><td>0.35</td><td>0.42</td><td>0.53</td></tr>
</tbody></table></div>
<p class="src">Source: BRIEF.md corrections (dQ_P32 column and PR_V from analyze_channelization.py).</p>
{AXBAR}
{sw("channel_active_area_","tcap","Active surface area 100 dQ/P32 through time, rows chemistries, columns P32.","Active surface area, one line per &sigma; (median over 5 seeds, 10&ndash;90 % band). Look at the starting level, which drops as P32 rises, and at the dip while the channel forms.")}
{sw("channel_pr_vol_","tcap","Volume-weighted participation ratio through time, rows chemistries, columns P32.","Volume-weighted participation ratio PR<sub>V</sub>, same layout. Look at the starting level, which rises with P32, and at how far each chemistry dips. Rows are the two chemistries, columns the P32 levels.")}
<div class="col"><p><strong>Sigma (paired networks with identical geometry).</strong> &sigma; = 1 starts with lower PR<sub>V</sub> than &sigma; = 0 in 13 of 15 seeds (median &minus;0.033). At the minimum the gap shrinks to &minus;0.016 (gypsum-only) and &minus;0.024 (coupled).</p></div>
<h3 id="stages">5c. The four stages</h3>
<div class="col"><p>The two participation ratios, the outlet dissolution and the front position, read together, give four stages (source: phase1_mechanism.csv and phase1_mechanism_summary.csv).</p></div>
{cartoon("four_stages")}
<div class="tablewrap"><table>
<thead><tr><th class="l">Stage</th><th class="l">t<sub>cap</sub></th><th class="l">What happens</th></tr></thead>
<tbody>
<tr><td class="l">1</td><td class="l">0&ndash;0.1</td><td class="l wrap">Pore space opens near the inlet; flow still spread over filled fractures. PR<sub>pore</sub> falls (for example 0.36 to 0.20) while PR<sub>V</sub> barely moves.</td></tr>
<tr><td class="l">2</td><td class="l">about 0.1&ndash;0.4</td><td class="l wrap">The front advances down the inherited paths. PR<sub>pore</sub> minimum at t<sub>cap</sub> 0.1&ndash;0.3.</td></tr>
<tr><td class="l">3</td><td class="l">about 0.4&ndash;0.6</td><td class="l wrap">Breakthrough: the outlet goes sharply from undissolved to more than 50 % dissolved. PR<sub>V</sub> minimum just before. PR<sub>pore</sub> back near its start (0.9&ndash;1.2 of it).</td></tr>
<tr><td class="l">4</td><td class="l">later</td><td class="l wrap">Widening: both ratios recover.</td></tr>
</tbody></table></div>
<div class="col"><p>Breakthrough is expensive. When the outlet passes 50 %, the network has dissolved 53&ndash;57 % (gypsum-only) and 58&ndash;67 % (coupled) of its gypsum. The range over runs is 31&ndash;82 %. Porosity 0.05 runs so far: 0.49&ndash;0.62.</p></div>
{AXBAR}
{sw("mechanism_gyponly_","tcap","Gypsum-only mechanism figure: PR_V, PR_pore, outlet dissolution and front position through time.","Gypsum-only. Look at PR<sub>pore</sub> dipping first, then the outlet jumping while PR<sub>V</sub> bottoms out. One line per &sigma;, columns P32.",1760)}
{sw("mechanism_gypcal_","tcap","Coupled mechanism figure with the same four measures.","Coupled. Same sequence with a shallower PR<sub>V</sub> minimum.",1760)}
<div class="col"><p><strong>Reading the maps.</strong> Each fracture is coloured by two things: how open it is and how much flow it carries. <em>Open channel</em>: open space and high flow. <em>Open space, little flow</em>: dissolved but bypassed. <em>Flow through filled rock</em>: carries flow but is still mostly mineral. <em>Filled, idle</em>: neither. The leading edge marks where flow paths are at least 50 % dissolved (100 m average).</p></div>
<div class="pair">
<figure><video controls loop muted playsinline preload="metadata" src="img/anim2/movie_gyponly.mp4"></video><figcaption>Gypsum-only run through the four stages. Watch the open channel grow from the inlet along the paths that already carry flow.</figcaption></figure>
<figure><video controls loop muted playsinline preload="metadata" src="img/anim2/movie_gypcal.mp4"></video><figcaption>Coupled run, same view. Compare the width of the open channel at breakthrough with the gypsum-only case.</figcaption></figure>
</div>
{fig("anim2/stages_gyponly.png","Contact sheet of four stages, gypsum-only.","Gypsum-only, one frame per stage (1 to 4, left to right). Look at the open channel in stage 3.")}
{fig("anim2/stages_gypcal.png","Contact sheet of four stages, coupled.","Coupled, one frame per stage. Look at how much rock stays filled around the channel.")}
<h3>5d. Inheritance</h3>
<div class="col"><p>The reaction sharpens paths that already existed. It does not open new ones. At the channel peak, 92&ndash;99 % of the fractures in the 90 %-flow set (median 97&ndash;99 %) were in the initial set.</p></div>
<div class="tablewrap"><table>
<thead><tr><th class="l">Quantity</th><th class="l">Value</th></tr></thead>
<tbody>
<tr><td class="l">Inheritance at the channel peak</td><td class="l">92&ndash;99 % (median 97&ndash;99 %)</td></tr>
<tr><td class="l">Dip around breakthrough</td><td class="l">to about 0.95&ndash;0.97, then back to 1</td></tr>
<tr><td class="l">Jaccard overlap, gypsum-only vs coupled sets</td><td class="l">0.75&ndash;0.93 (median about 0.82)</td></tr>
<tr><td class="l">Phase 2, &times;20 ceiling</td><td class="l">0.95&ndash;0.99</td></tr>
<tr><td class="l">Phase 2, 2 mM coupled</td><td class="l">0.97&ndash;0.99</td></tr>
</tbody></table></div>
<p class="src">Source: forsmark_reactive/phase1/phase1_channel_identity.csv; Phase 2 rows from BRIEF.md (early Phase 2, 3 seeds).</p>
{AXBAR}
{sw("inheritance_","tcap","Share of the current 90 %-flow set that was in the initial set, through time.","Inheritance through time. Look at how close the lines stay to 1 and at the small dip near breakthrough.",1750)}
<h3>5e. Transport</h3>
<div class="col"><p>While the channel forms, the median arrival time moves closer to the mean residence time. For gypsum-only runs, median arrival divided by \\(\\tau_\\mathrm{{res}}\\) rises from about 0.79&ndash;0.87 to 0.91&ndash;0.95. The tail exponent steepens from about 3.1&ndash;3.7 to 4.0&ndash;4.5. The dispersivity falls. All three recover once the channel has dissolved through.</p></div>
{cartoon("transport")}
<div class="tablewrap"><table>
<thead><tr><th class="l">Example: P32 &times;6, &sigma; = 1, seed 1, gypsum-only</th><th>unreacted</th><th>channel peak</th><th>after widening</th></tr></thead>
<tbody>
<tr><td class="l">median arrival / &tau;<sub>res</sub></td><td>0.64</td><td>0.85</td><td>0.77</td></tr>
<tr><td class="l">tail exponent &gamma;</td><td>2.4</td><td>3.3</td><td>2.6</td></tr>
</tbody></table></div>
<p class="src">Source: BRIEF.md; forsmark_reactive/phase1/phase1_tracer.csv.</p>
{fig("tracer_btc_annotated_gyponly.png","Breakthrough curves for the example network at three stages, gypsum-only.","Breakthrough curves f(t) for the example network, time divided by the current mean residence time. Look at the red curve (channel peak): its median moves right and its tail is steeper than the grey (unreacted) and blue (after widening) curves.")}
{fig("tracer_btc_annotated_gypcal.png","Breakthrough curves for the example network, coupled.","Same example network, coupled run.")}
<div class="pending">These are coarse probes. Finer probes are being folded in overnight, so the figures below may change.</div>
{AXBAR}
{sw("tracer_metrics_gyponly_","tcap","Tracer metrics through time, gypsum-only.","Gypsum-only tracer metrics (arrival, tail exponent, dispersivity) through time. Look at the excursion during channel formation and the return afterwards.",1760)}
{sw("tracer_metrics_gypcal_","tcap","Tracer metrics through time, coupled.","Coupled tracer metrics, same layout.",1760)}
</section>''')

# ---------- 6 candidates
A(f'''<section id="candidates">
<h2>6. Candidate findings</h2>
{S("<p>These five items are results that look new to us, but each rests on limited tests. For each we give the claim, a cartoon of the idea, the data, what could make it wrong, and its status. None is established yet.</p>")}
<div class="item"><h3>6.1 Flow and pore space decouple, then realign</h3>
<p class="claim">In mineral-filled networks, flow focusing measured against open pore volume and against fracture volume bottom out at different times.</p>
{cartoon("decoupling")}
<p><strong>Data.</strong> PR<sub>pore</sub> bottoms out first (t<sub>cap</sub> 0.1&ndash;0.3), PR<sub>V</sub> at breakthrough (0.4&ndash;0.6). In open fractures both are the same quantity, so this does not occur there.</p>
{fig("decoupling_scatter_gyponly.png","Per-fracture flow share against open pore volume share at four stages, gypsum-only.","Each dot is one fracture (P32 &times;6, &sigma; = 1, seed 1). The line is flow in proportion to open space. Look at the cloud sitting below the line at stage 1 (space without flow) and moving toward the line by stage 4.")}
{fig("decoupling_scatter_gypcal.png","Per-fracture flow share against open pore volume share at four stages, coupled.","Same view for the coupled run.")}
<p><strong>What could make it wrong.</strong> BiGraFV caveat: a long fracture opens along its whole length at once, so the offset may be model-dependent. <strong>Status.</strong> Candidate.</p></div>

<div class="item"><h3>6.2 Channelization narrows transport</h3>
<p class="claim">Because the dissolved channel is where the pore space is, the breakthrough curve tightens and its tail steepens while the channel forms.</p>
<p><strong>Data.</strong> Section 5e: median arrival/&tau;<sub>res</sub> 0.79&ndash;0.87 to 0.91&ndash;0.95; &gamma; 3.1&ndash;3.7 to 4.0&ndash;4.5 (gypsum-only). Cartoon in section 5e.</p>
<p><strong>What could make it wrong.</strong> Coarse Eulerian probes with numerical dispersion; the &gamma; fit window is our choice; the one-cell model is an approximation. <strong>Status.</strong> Candidate; finer probes running.</p></div>

<div class="item"><h3>6.3 A compact front, not a wormhole, at kilometre scale</h3>
<p class="claim">The dissolution front advances as a broad front over many parallel paths. It does not run away as a thin finger.</p>
{cartoon("front_vs_wormhole")}
<p><strong>Data.</strong> Breakthrough costs 53&ndash;57 % (gypsum-only) and 58&ndash;67 % (coupled) of the gypsum (medians; 31&ndash;82 % over runs). A wormhole would break through after a few percent. Network argument: 9&ndash;44 parallel paths over 1 km and a gain capped at &times;10&ndash;&times;20.</p>
{fig("breakthrough_dissolved.png","Gypsum dissolved when the front reaches the outlet, by P32 and chemistry.","Each dot is one run; bars are medians; squares are porosity 0.05. Look at how far all values sit above the grey wormhole-like band (a few percent).")}
<p><strong>What could make it wrong (BiGraFV caveats).</strong> One cell per fracture means no in-plane fronts or wormholes by construction, and a long fracture opens along its whole length at once. On smaller paired networks, meshed DFNs channelized more than the one-cell graph (n90 ratio 0.79 vs 0.94 and 0.84 vs 0.88 on two dense networks), and graph channel timing lagged at strong k&ndash;&phi; feedback. The network-scale argument applies to a meshed DFN too, but front sharpness may be model-dependent. <strong>Status.</strong> Candidate, model-dependent.</p></div>

<div class="item"><h3>6.4 A channel-depth law</h3>
<p class="claim">The depth of the channel (PR<sub>V</sub> minimum divided by its start) is set by the permeability gain the reaction can reach, not by the chemistry.</p>
{cartoon("depth_law")}
<p><strong>Data.</strong> Phase 1: PR<sub>V</sub> minimum over start is about 0.64&ndash;0.67 for gypsum-only and 0.77&ndash;0.79 for coupled, at every P32 and &sigma; (phase1_channel_minima.csv). Early Phase 2 (&sigma; = 1, seeds 1&ndash;3), channel depth:</p>
<div class="tablewrap"><table>
<thead><tr><th class="l">Ceiling and case</th><th>P32 &times;4</th><th>&times;6</th><th>&times;8</th></tr></thead>
<tbody>
<tr><td class="l">&times;10, gypsum-only</td><td>0.695</td><td>0.678</td><td>0.656</td></tr>
<tr><td class="l">&times;10.6, coupled, &phi;<sub>0</sub> 0.05</td><td>0.694</td><td>0.672</td><td>0.665</td></tr>
<tr><td class="l">about &times;10, coupled 2 mM</td><td>0.701</td><td>0.675</td><td>&ndash; (not yet)</td></tr>
<tr><td class="l">&times;5.5, coupled</td><td>0.779</td><td>0.760</td><td>0.799</td></tr>
<tr><td class="l">&times;20, gypsum-only, &phi;<sub>0</sub> 0.05</td><td>0.625</td><td>0.601</td><td>&ndash; (not yet)</td></tr>
</tbody></table></div>
<p class="src">Source: BRIEF.md (early Phase 2; Phase 2 CSVs still filling).</p>
<p>Equal ceilings give equal depth within about 0.01 whatever the chemistry.</p>
{fig("depth_law.png","Channel depth against permeability ceiling for the two chemistries and two porosities.","Channel depth (PR<sub>V</sub> minimum over start) against the n = 1 permeability ceiling. Look at the points at &times;10: blue (gypsum-only) and orange (coupled, porosity 0.05) overlap; &times;5.5 sits higher and &times;20 lower.")}
<p><strong>What could make it wrong.</strong> Three seeds per case; the &times;20 and &times;5.5 comparisons also change porosity or chemistry together with the ceiling. <strong>Status.</strong> Candidate; Phase 2 running.</p></div>

<div class="item"><h3>6.5 Precipitation rerouting</h3>
<p class="claim">Calcite forming just downstream of the dissolving zone could narrow the open path and push flow onto a neighbour.</p>
{cartoon("precipitation_reroute")}
<p><strong>Data.</strong> The 2 mM carbonate test (capacity matched to gypsum-only) shows no rerouting yet: channel depth matches gypsum-only and inheritance is 0.97&ndash;0.99. <strong>What could make it wrong.</strong> The test is early and 3 seeds only; a null result so far. <strong>Status.</strong> Untested beyond the first runs; hypothesis only.</p></div>
</section>''')

# ---------- 7 new
A('''<section id="new">
<h2>7. What is new and what is not</h2>
<div class="summary"><span class="tag">In plain words</span><p>Most of the physical picture agrees with recent published work, now shown at 1 km. The five candidates in section 6 are what we think may be new. We found no published reactive study with thousands of fractures at this scale.</p></div>
<div class="col">
<p><strong>Known and consistent.</strong></p>
<ul>
<li>Network channels follow the initial structure. Hyman et al. (2026): several parallel inlet-to-outlet channels enlarge along their whole length, and the networks are already strongly channelized at &tau; = 0. Szawe&#322;&#322;o et al. (2026): uniform dissolution cannot remove the heterogeneity set by network topology. Here, 92&ndash;99 % of the channel fractures were already in the initial set, at 1 km with 1,587 to 4,070 fractures.</li>
<li>Replacement by calcite limits the permeability gain through the solid-volume ratio &Gamma; (Budek &amp; Szymczak 2025; Budek et al. 2026). Our &times;5.5 ceiling is arithmetic on that ratio, not a finding.</li>
<li>Reaction partly (not fully) removes heterogeneity (Hyman et al. 2026; Szawe&#322;&#322;o et al. 2026).</li>
</ul>
<p><strong>Candidates for new.</strong> (1) Flow and pore-space decoupling in mineral-filled networks. (2) Channelization narrowing transport. (3) A compact front at kilometre scale. (4) A channel-depth law set by the achievable permeability contrast. (5) Precipitation rerouting (2 mM test).</p>
<p><strong>Literature context.</strong> The largest reactive graph study we found is 25 m with about 526 fractures (Hyman et al. 2026); meshed DFNs are 10 m. The only coupled 3D DFN dissolution-precipitation study is Hyman et al. (2024a), at 10 m. Hyman et al. (2026, graph) is dissolution-only. We found no km-scale reactive DFN with thousands of fractures. BiGraFV itself is unpublished.</p>
</div>
</section>''')

# ---------- 8 limits
A('''<section id="limits">
<h2>8. Limits and decisions for the user</h2>
<div class="summary"><span class="tag">In plain words</span><p>Some results depend on modelling choices that we could not check against a published source. Three need a decision from you: the transmissivity law, the pore-volume convention, and the capacity bound.</p></div>
<div class="col"><ul>
<li><strong>BiGraFV caveats.</strong> One control volume per fracture: no in-plane fronts or wormholes; a long fracture opens along its whole length at once; dead ends only approximate. On smaller paired TPL networks meshed DFNs channelized more than the one-cell graph (n90 ratio 0.79 vs 0.94 and 0.84 vs 0.88), and graph timing lagged at strong k&ndash;&phi; feedback.</li>
<li><strong>Decision: transmissivity depth.</strong> Rebuild the networks with the depth-consistent 200&ndash;400 m law (semi-correlated 1.3&times;10<sup>&minus;9</sup> r<sup>0.5</sup>, or correlated 1.6&times;10<sup>&minus;9</sup> r<sup>0.8</sup>)? The two laws differ about 190 times at r = 100 m. Fixed Q makes absolute T irrelevant, but the size-T contrast is not.</li>
<li><strong>Decision: one pore volume per year.</strong> Hyman et al. (2024b) do not say whether &ldquo;volume&rdquo; is bulk or pore volume. We chose pore volume. The alternative would be 10 times our rate per unit bulk volume.</li>
<li><strong>c<sub>cap</sub> is an upper bound.</strong> It assumes saturated outflow. The brine pilot measured about 470 against 516.6 mol/m&sup3; (about 9 % lower). At low Damk&ouml;hler number the dissolved fraction is below t<sub>cap</sub>.</li>
<li><strong>Tail-fit window.</strong> The window [2 t<sub>peak</sub>, t at f = 10<sup>&minus;2</sup> f<sub>peak</sub>] is ours. Hyman et al. (2026) give no window.</li>
<li><strong>Eulerian probes.</strong> The tracer runs on a frozen field with numerical dispersion; first arrival is smeared. Arrivals are also divided by &tau;<sub>res</sub> because Q is fixed while the pore volume grows up to &times;10.</li>
<li><strong>Small samples.</strong> The depth-law table and the 2 mM result use sigma 1.0, seeds 1&ndash;3.</li>
</ul></div>
</section>''')

# ---------- 9 refs
refs = [
("Bell, R.J., Dean, P., Hibbins-Butler, D.C. (1970). Localization of normal modes in vitreous silica, germania and beryllium fluoride. <em>J. Phys. C</em> 3(10), 2111&ndash;2118.","10.1088/0022-3719/3/10/013"),
("Budek, A., Szymczak, P. (2025). Channeling, clogging and permeability oscillations: different macroscopic regimes in mineral replacement. <em>J. Geophys. Res. Solid Earth</em> 130(6), e2024JB031081.","10.1029/2024JB031081"),
("Budek, A., Szymczak, P., Kang, P.K. (2026). Fractures regulate coupled dissolution-precipitation dynamics: regime map, optimal fracture conductance, and clogging. <em>Earth Planet. Sci. Lett.</em> 690, 120163.","10.1016/j.epsl.2026.120163"),
("Edwards, J.T., Thouless, D.J. (1972). Numerical studies of localization in disordered systems. <em>J. Phys. C</em> 5(8), 807&ndash;820.","10.1088/0022-3719/5/8/007"),
("Fox, A., La Pointe, P., Hermanson, J., Oehman, J. (2007). Statistical geological discrete fracture network model, Forsmark modelling stage 2.2. SKB R-07-46.",None),
("Fredd, C.N., Fogler, H.S. (1998). Influence of transport and reaction on wormhole formation in porous media. <em>AIChE J.</em> 44(9), 1933&ndash;1949.","10.1002/aic.690440902"),
("Hyman, J.D. (2020). Flow channeling in fracture networks: characterizing the effect of density on preferential flow path formation. <em>Water Resour. Res.</em> 56(9), e2020WR027986.","10.1029/2020WR027986"),
("Hyman, J.D., Karra, S., Makedonska, N., Gable, C.W., Painter, S.L., Viswanathan, H.S. (2015). dfnWorks: a discrete fracture network framework for modeling subsurface flow and transport. <em>Comput. Geosci.</em> 84, 10&ndash;19.","10.1016/j.cageo.2015.08.001"),
("Hyman, J.D., Murph, A.C., Boampong, L., Navarre-Sitchler, A., Carey, J.W., Stauffer, P., Viswanathan, H.S. (2024a). Determining the dominant factors controlling mineralization in three-dimensional fracture networks. <em>Int. J. Greenh. Gas Control</em> 139, 104265.","10.1016/j.ijggc.2024.104265"),
("Hyman, J.D., Navarre-Sitchler, A., Sweeney, M.R., Pachalieva, A., Carey, J.W., Viswanathan, H.S. (2024b). Quartz dissolution effects on flow channelization and transport behavior in three-dimensional fracture networks. <em>Geochem. Geophys. Geosyst.</em> 25(7), e2024GC011550.","10.1029/2024GC011550"),
("Hyman, J.D., Szawe&#322;&#322;o, T., Kang, P.K., Szymczak, P. (2026). Effects of dissolution regimes on flow channelization and solute transport in 3D fracture networks: insights from graph-based reactive transport modeling. <em>J. Geophys. Res. Solid Earth</em> 131(3), e2025JB033004.","10.1029/2025JB033004"),
("Kreft, A., Zuber, A. (1978). On the physical meaning of the dispersion equation and its solutions for different initial and boundary conditions. <em>Chem. Eng. Sci.</em> 33(11), 1471&ndash;1480.","10.1016/0009-2509(78)85196-3"),
("Lichtner, P.C. et al. (2015). PFLOTRAN User Manual and Theory Guide. documentation.pflotran.org.",None),
("Maillot, J., Davy, P., Le Goc, R., Darcel, C., de Dreuzy, J.-R. (2016). Connectivity, permeability, and channeling in randomly distributed and kinematically defined discrete fracture network models. <em>Water Resour. Res.</em> 52(11), 8526&ndash;8545.","10.1002/2016WR018973"),
("Sahimi, M. (2011). <em>Flow and Transport in Porous Media and Fractured Rock</em>, 2nd ed. Wiley-VCH, Weinheim.","10.1002/9783527636693"),
("SKB (2010). Data report for the safety assessment SR-Site. TR-10-52, Table 6-75.",None),
("Szawe&#322;&#322;o, T., Hyman, J.D., Kang, P.K., Szymczak, P. (2026). Structural barriers to complete homogenization and wormholing in dissolving porous and fractured rocks. <em>Int. J. Rock Mech. Min. Sci.</em> 200, 106431.","10.1016/j.ijrmms.2026.106431"),
("Szymczak, P., Ladd, A.J.C. (2009). Wormhole formation in dissolving fractures. <em>J. Geophys. Res.</em> 114, B06203.","10.1029/2008JB006122"),
("Szymczak, P., Ladd, A.J.C. (2012). Reactive infiltration instabilities in rocks. Fracture dissolution. <em>J. Fluid Mech.</em> 702, 239&ndash;264.","10.1017/jfm.2012.174"),
("BiGraFV: this work, unpublished.",None),
]
items = []
for t, doi in refs:
    d = f' <a href="https://doi.org/{doi}">doi:{doi}</a>' if doi else ""
    items.append(f"<li>{t}{d}</li>")
A('<section id="refs"><h2>9. References</h2><div class="summary"><span class="tag">In plain words</span><p>In the text, sources appear as (Author year). Items marked unpublished or without a DOI are given as in the source records.</p></div><ol class="refs">' + "\n".join(items) + '</ol></section>')

# ---------- 10 appendix
A('''<section id="appendix">
<h2>10. Appendix: runs and files</h2>
<div class="summary"><span class="tag">In plain words</span><p>Phase 1 is complete. Phase 2 and the P32 &times;16 set are running and will be added when they finish.</p></div>
<div class="tablewrap"><table>
<thead><tr><th class="l">Set</th><th class="l">Content</th><th class="l">Status</th></tr></thead>
<tbody>
<tr><td class="l">Phase 1</td><td class="l">45 networks &times; {gypsum-only, coupled} = 90 runs, to 36,515 PV</td><td class="l">complete</td></tr>
<tr><td class="l">Phase 2</td><td class="l">&sigma; = 1.0, seeds 1&ndash;3, P32 &times;4/&times;6/&times;8/&times;16. Initial porosity 0.05 (gypsum-only and coupled, 0.5 M); coupled 2 mM carbonate at porosity 0.1 (capacity matched to gypsum-only). Run to capacity time 2.</td><td class="l">running</td></tr>
<tr><td class="l">P32 &times;16</td><td class="l">15 networks &times; 2 chemistries, to capacity time 2</td><td class="l">running</td></tr>
</tbody></table></div>
<div class="col"><p>Paths are relative to <code>src/alpha_study/forsmark_reactive/</code>.</p>
<ul>
<li>Data: <code>phase1/phase1_end_summary.csv</code>, <code>phase1_channel_minima.csv</code>, <code>phase1_channel_identity.csv</code>, <code>phase1_mechanism.csv</code>, <code>phase1_mechanism_summary.csv</code>, <code>phase1_tracer.csv</code>, <code>phase1/network_stats.json</code>.</li>
<li>Code: <code>time_axes.py</code> (three clocks), <code>analyze_channelization.py</code> (participation ratios), <code>network_forsmark.py</code>, <code>build_km_graph_network.py --forsmark</code>, <code>exfix_outflow.py</code>.</li>
<li>Figures: <code>report_phase1/img/</code>; tracer figures from <code>phase1/figures/</code>; cartoons in <code>report_phase1/cartoons/</code>.</li>
</ul></div>
</section>''')

HEAD = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Forsmark Reactive Channels</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']]}},svg:{{fontCache:'global'}}}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"></script>
<style>{CSS}</style>
</head>
<body>
<main>
'''
html = HEAD + "\n".join(body) + f'\n</main>\n<script>{JS}</script>\n</body>\n</html>\n'
open(f"{D}/index.html","w").write(html)
print(len(html))
