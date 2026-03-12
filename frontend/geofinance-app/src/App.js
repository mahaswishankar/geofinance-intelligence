// src/App.js - GeoFinance Intelligence Platform v3 - GeoTrade Style
import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from "recharts";

const API = "http://localhost:5000";
const GEO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const NUMERIC_TO_CODE = {
  "004":"AF","008":"AL","010":"AQ","012":"DZ","024":"AO","031":"AZ",
  "032":"AR","036":"AU","040":"AT","044":"BS","050":"BD","051":"AM",
  "056":"BE","064":"BT","068":"BO","070":"BA","072":"BW","076":"BR",
  "084":"BZ","090":"SB","096":"BN","100":"BG","104":"MM","108":"BI",
  "112":"BY","116":"KH","120":"CM","124":"CA","140":"CF","144":"LK",
  "148":"TD","152":"CL","156":"CN","158":"TW","170":"CO","178":"CG",
  "180":"CD","188":"CR","191":"HR","192":"CU","196":"CY","203":"CZ",
  "204":"BJ","208":"DK","214":"DO","218":"EC","222":"SV","226":"GQ",
  "231":"ET","232":"ER","233":"EE","238":"FK","242":"FJ","246":"FI",
  "250":"FR","260":"TF","262":"DJ","266":"GA","268":"GE","270":"GM",
  "275":"PS","276":"DE","288":"GH","300":"GR","304":"GL","320":"GT",
  "324":"GN","328":"GY","332":"HT","340":"HN","348":"HU","352":"IS",
  "356":"IN","360":"ID","364":"IR","368":"IQ","372":"IE","376":"IL",
  "380":"IT","384":"CI","388":"JM","392":"JP","398":"KZ","400":"JO",
  "404":"KE","408":"KP","410":"KR","414":"KW","417":"KG","418":"LA",
  "422":"LB","426":"LS","428":"LV","430":"LR","434":"LY","440":"LT",
  "442":"LU","450":"MG","454":"MW","458":"MY","466":"ML","478":"MR",
  "484":"MX","496":"MN","498":"MD","499":"ME","504":"MA","508":"MZ",
  "512":"OM","516":"NA","524":"NP","528":"NL","540":"NC","548":"VU",
  "554":"NZ","558":"NI","562":"NE","566":"NG","578":"NO","586":"PK",
  "591":"PA","598":"PG","600":"PY","604":"PE","608":"PH","616":"PL",
  "620":"PT","624":"GW","626":"TL","630":"PR","634":"QA","642":"RO",
  "643":"RU","646":"RW","682":"SA","686":"SN","688":"RS","694":"SL",
  "703":"SK","704":"VN","705":"SI","706":"SO","710":"ZA","716":"ZW",
  "724":"ES","728":"SS","729":"SD","732":"EH","740":"SR","748":"SZ",
  "752":"SE","756":"CH","760":"SY","762":"TJ","764":"TH","768":"TG",
  "780":"TT","784":"AE","788":"TN","792":"TR","795":"TM","800":"UG",
  "804":"UA","807":"MK","818":"EG","826":"GB","834":"TZ","840":"US",
  "854":"BF","858":"UY","860":"UZ","862":"VE","887":"YE","894":"ZM",
};

// Country to primary asset mapping (for Geo Map candlestick)
const COUNTRY_ASSET = {
  RU: { ticker: "USO", label: "Oil (Crude)" },
  SA: { ticker: "USO", label: "Oil (Crude)" },
  IR: { ticker: "USO", label: "Oil (Crude)" },
  IQ: { ticker: "USO", label: "Oil (Crude)" },
  CN: { ticker: "EEM", label: "Emerging Markets" },
  US: { ticker: "SPY", label: "S&P 500" },
  DE: { ticker: "SPY", label: "S&P 500" },
  GB: { ticker: "SPY", label: "S&P 500" },
  JP: { ticker: "SPY", label: "S&P 500" },
  IN: { ticker: "EEM", label: "Emerging Markets" },
  UA: { ticker: "GLD", label: "Gold (Safe Haven)" },
  IL: { ticker: "GLD", label: "Gold (Safe Haven)" },
  SY: { ticker: "GLD", label: "Gold (Safe Haven)" },
  YE: { ticker: "USO", label: "Oil (Crude)" },
  VE: { ticker: "USO", label: "Oil (Crude)" },
  KP: { ticker: "GLD", label: "Gold (Safe Haven)" },
};

const RISK_COLOR = (score) => {
  if (!score && score !== 0) return "#1a2035";
  if (score < 25) return "#00c853";
  if (score < 50) return "#ffd600";
  if (score < 75) return "#ff6d00";
  return "#d50000";
};

const RISK_BG = (score) => {
  if (!score && score !== 0) return "#0d1117";
  if (score < 25) return "#00c85318";
  if (score < 50) return "#ffd60018";
  if (score < 75) return "#ff6d0018";
  return "#d5000018";
};

// AI Signal data (static but realistic)
const AI_SIGNALS = [
  {
    ticker: "XAU/USD", name: "Gold", category: "Commodities / Global",
    signal: "BUY", confidence: 88, bullish: 70, bearish: 30,
    volatility: "MEDIUM", timeframe: "Short-term",
    trigger: "Iran-Israel Escalation — Missile Exchanges",
    entry: 2341.00, target: 2427.00, stop: 2290.00,
    riskReward: "2.80x", winRate: "1.84%", maxPnL: "3.2%",
    color: "#00c853"
  },
  {
    ticker: "WTI", name: "Crude Oil", category: "Commodities / Energy",
    signal: "BUY", confidence: 82, bullish: 75, bearish: 25,
    volatility: "HIGH", timeframe: "Short-term",
    trigger: "Strait of Hormuz Naval Blockade Risk",
    entry: 82.40, target: 91.00, stop: 78.50,
    riskReward: "2.20x", winRate: "2.10%", maxPnL: "4.8%",
    color: "#00c853"
  },
  {
    ticker: "LMT", name: "Lockheed Martin", category: "Defense / US",
    signal: "BUY", confidence: 85, bullish: 80, bearish: 20,
    volatility: "LOW", timeframe: "Medium-term",
    trigger: "NATO-Russia Border Pressure — Defense Posture",
    entry: 478.20, target: 520.00, stop: 455.00,
    riskReward: "1.94x", winRate: "3.20%", maxPnL: "5.1%",
    color: "#00c853"
  },
  {
    ticker: "SPX", name: "S&P 500", category: "Equities",
    signal: "SELL", confidence: 68, bullish: 35, bearish: 65,
    volatility: "HIGH", timeframe: "Short-term",
    trigger: "Risk-Off Sentiment — Flight to Safety",
    entry: 5520.00, target: 5280.00, stop: 5640.00,
    riskReward: "2.00x", winRate: "1.60%", maxPnL: "2.9%",
    color: "#ff1744"
  },
  {
    ticker: "EUR/USD", name: "Euro / Dollar", category: "Forex / Europe",
    signal: "SELL", confidence: 72, bullish: 30, bearish: 70,
    volatility: "MEDIUM", timeframe: "Short-term",
    trigger: "Russia-Europe Energy Flow Disruption",
    entry: 1.0820, target: 1.0540, stop: 1.0960,
    riskReward: "2.00x", winRate: "1.90%", maxPnL: "2.6%",
    color: "#ff1744"
  },
  {
    ticker: "BTC/USD", name: "Bitcoin", category: "Crypto / Global",
    signal: "HOLD", confidence: 58, bullish: 50, bearish: 50,
    volatility: "VERY HIGH", timeframe: "Medium-term",
    trigger: "Mixed signals — Geopolitical uncertainty vs institutional demand",
    entry: 82400, target: 91000, stop: 74000,
    riskReward: "1.04x", winRate: "1.10%", maxPnL: "1.8%",
    color: "#ffd600"
  },
];

// Simple candlestick-style chart using bars
function CandlestickChart({ data }) {
  if (!data || data.length === 0) return <div style={{ color: "#444", textAlign: "center", paddingTop: 80 }}>No data available</div>;
  const recent = data.slice(-40);
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={recent} barCategoryGap="20%">
        <XAxis dataKey="date" tick={{ fill: "#444", fontSize: 9 }} tickFormatter={d => d?.slice(5)} interval={7} />
        <YAxis tick={{ fill: "#444", fontSize: 9 }} domain={["auto", "auto"]} tickFormatter={v => `$${v}`} width={55} />
        <Tooltip
          contentStyle={{ background: "#0a0e1a", border: "1px solid #00d4ff33", borderRadius: 8 }}
          labelStyle={{ color: "#00d4ff" }}
          itemStyle={{ color: "#fff" }}
          formatter={v => [`$${Number(v).toFixed(2)}`, "Price"]}
        />
        <Bar dataKey="close" radius={[2, 2, 0, 0]}>
          {recent.map((entry, i) => {
            const prev = recent[i - 1];
            const up = !prev || entry.close >= prev.close;
            return <Cell key={i} fill={up ? "#00c853" : "#ff1744"} />;
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// 3D Globe — deep space, embossed countries, glowing great-circle arcs
function Globe3D({ allRisks, onCountryClick, selectedCode }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const rotationRef = useRef([0, -20]);
  const isDragging = useRef(false);
  const lastPos = useRef([0, 0]);
  const geoDataRef = useRef(null);
  const d3Ref = useRef(null);
  const allRisksRef = useRef(allRisks);
  const selectedCodeRef = useRef(selectedCode);
  const starsRef = useRef([]);
  const frameRef = useRef(0);

  useEffect(() => { allRisksRef.current = allRisks; }, [allRisks]);
  useEffect(() => { selectedCodeRef.current = selectedCode; }, [selectedCode]);

  function genStars(W, H) {
    const arr = [];
    for (let i = 0; i < 350; i++) {
      arr.push({
        x: Math.random() * W, y: Math.random() * H,
        r: Math.random() * 1.4 + 0.1,
        o: Math.random() * 0.7 + 0.15,
        twinkle: Math.random() * Math.PI * 2
      });
    }
    return arr;
  }

  useEffect(() => {
    const loadLibs = async () => {
      if (!window.d3) await new Promise(res => { const s = document.createElement("script"); s.src = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"; s.onload = res; document.head.appendChild(s); });
      if (!window.topojson) await new Promise(res => { const s = document.createElement("script"); s.src = "https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"; s.onload = res; document.head.appendChild(s); });
      d3Ref.current = window.d3;
      const topo = await fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(r => r.json());
      geoDataRef.current = window.topojson.feature(topo, topo.objects.countries);
      const canvas = canvasRef.current;
      if (canvas) { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; starsRef.current = genStars(canvas.width, canvas.height); }
      const animate = () => {
        frameRef.current++;
        if (!isDragging.current) rotationRef.current = [rotationRef.current[0] - 0.08, rotationRef.current[1]];
        drawFrame();
        animRef.current = requestAnimationFrame(animate);
      };
      animate();
    };
    loadLibs();
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  function getProjection(canvas) {
    const R = Math.min(canvas.width, canvas.height) * 0.41;
    return d3Ref.current.geoOrthographic().scale(R).translate([canvas.width / 2, canvas.height / 2]).rotate(rotationRef.current).clipAngle(90);
  }

  // Parse hex color to rgb
  function hexRgb(hex) {
    return [parseInt(hex.slice(1,3),16), parseInt(hex.slice(3,5),16), parseInt(hex.slice(5,7),16)];
  }

  function drawFrame() {
    const canvas = canvasRef.current;
    if (!canvas || !d3Ref.current || !geoDataRef.current) return;
    const d3 = d3Ref.current;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const cx = W / 2, cy = H / 2;
    const proj = getProjection(canvas);
    const R = proj.scale();
    const path = d3.geoPath(proj, ctx);
    const frame = frameRef.current;

    // === DEEP SPACE BACKGROUND ===
    const spaceBg = ctx.createRadialGradient(cx * 0.6, cy * 0.5, 0, cx, cy, Math.max(W, H));
    spaceBg.addColorStop(0, "#03070f");
    spaceBg.addColorStop(0.5, "#010305");
    spaceBg.addColorStop(1, "#000102");
    ctx.fillStyle = spaceBg;
    ctx.fillRect(0, 0, W, H);

    // === TWINKLING STARS ===
    starsRef.current.forEach(s => {
      const dx = s.x - cx, dy = s.y - cy;
      if (Math.sqrt(dx*dx + dy*dy) < R + 8) return; // skip inside globe
      const twinkle = 0.7 + 0.3 * Math.sin(s.twinkle + frame * 0.02);
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r * twinkle, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(190,215,255,${s.o * twinkle})`;
      ctx.fill();
    });

    // === GREAT CIRCLE ARCS over space (drawn BEFORE globe clip) ===
    // These arcs are ellipses tilted at angles — they pass over and behind the globe
    const arcDefs = [
      { rx: R * 1.38, ry: R * 0.28, rot: -0.35, color: "rgba(0,212,255,0.18)", dash: [12,22], speed: 0.6 },
      { rx: R * 1.22, ry: R * 0.22, rot:  0.55, color: "rgba(0,180,255,0.12)", dash: [8,28],  speed: -0.45 },
      { rx: R * 1.55, ry: R * 0.18, rot: -0.15, color: "rgba(80,180,255,0.08)", dash: [16,30], speed: 0.3 },
      { rx: R * 1.30, ry: R * 0.35, rot:  1.1,  color: "rgba(0,200,255,0.10)", dash: [6,20],  speed: -0.7 },
    ];
    arcDefs.forEach(({ rx, ry, rot, color, dash, speed }) => {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(rot);
      ctx.beginPath();
      ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.0;
      ctx.setLineDash(dash);
      ctx.lineDashOffset = -(frame * speed);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();
    });

    // === GLOBE — clip everything inside sphere ===
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.clip();

    // Ocean — deep blue gradient
    const ocean = ctx.createRadialGradient(cx - R * 0.25, cy - R * 0.3, R * 0.1, cx + R * 0.1, cy + R * 0.1, R * 1.2);
    ocean.addColorStop(0, "#0e2d55");
    ocean.addColorStop(0.45, "#071a35");
    ocean.addColorStop(1, "#020a18");
    ctx.fillStyle = ocean;
    ctx.fillRect(0, 0, W, H);

    // Graticule (subtle)
    ctx.beginPath();
    path(d3.geoGraticule()());
    ctx.strokeStyle = "rgba(0,140,255,0.07)";
    ctx.lineWidth = 0.4;
    ctx.stroke();

    // === COUNTRIES — draw base fill ===
    geoDataRef.current.features.forEach(feature => {
      const numId = feature.id?.toString().padStart(3, "0");
      const code = NUMERIC_TO_CODE[numId];
      const risk = code ? allRisksRef.current[code] : null;
      const score = risk?.risk_score;
      const isSelected = code && code === selectedCodeRef.current;

      ctx.beginPath();
      path(feature);

      let hex;
      if (isSelected) hex = "#00d4ff";
      else if (risk) hex = RISK_COLOR(score);
      else if (code) hex = "#1a3558";
      else hex = "#0b1a2e";

      ctx.fillStyle = hex + (isSelected ? "ee" : "cc");
      ctx.fill();
    });

    // === COUNTRY BORDERS — bright top-edge highlight for 3D emboss effect ===
    geoDataRef.current.features.forEach(feature => {
      const numId = feature.id?.toString().padStart(3, "0");
      const code = NUMERIC_TO_CODE[numId];
      const isSelected = code && code === selectedCodeRef.current;
      ctx.beginPath();
      path(feature);
      ctx.strokeStyle = isSelected ? "#00d4ff" : "rgba(255,255,255,0.12)";
      ctx.lineWidth = isSelected ? 1.8 : 0.6;
      ctx.stroke();
    });

    // === 3D LIGHTING — multi-layer for deep emboss ===
    // Layer 1: Strong specular highlight top-left (glossy sphere feel)
    const specular = ctx.createRadialGradient(cx - R * 0.42, cy - R * 0.38, 0, cx - R * 0.42, cy - R * 0.38, R * 0.85);
    specular.addColorStop(0, "rgba(255,255,255,0.13)");
    specular.addColorStop(0.3, "rgba(255,255,255,0.04)");
    specular.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = specular;
    ctx.fillRect(0, 0, W, H);

    // Layer 2: Dark vignette on right/bottom — deep shadow
    const shadow = ctx.createRadialGradient(cx + R * 0.35, cy + R * 0.3, R * 0.3, cx, cy, R);
    shadow.addColorStop(0, "rgba(0,0,0,0)");
    shadow.addColorStop(0.6, "rgba(0,0,0,0.15)");
    shadow.addColorStop(1, "rgba(0,0,0,0.65)");
    ctx.fillStyle = shadow;
    ctx.fillRect(0, 0, W, H);

    // Layer 3: Edge darkening all around (sphere curvature)
    const edge = ctx.createRadialGradient(cx, cy, R * 0.72, cx, cy, R);
    edge.addColorStop(0, "rgba(0,0,0,0)");
    edge.addColorStop(1, "rgba(0,0,10,0.55)");
    ctx.fillStyle = edge;
    ctx.fillRect(0, 0, W, H);

    ctx.restore(); // end globe clip

    // === ATMOSPHERE HALO (outside globe) ===
    const halo = ctx.createRadialGradient(cx, cy, R * 0.97, cx, cy, R * 1.18);
    halo.addColorStop(0, "rgba(20,100,255,0.22)");
    halo.addColorStop(0.4, "rgba(0,60,200,0.10)");
    halo.addColorStop(1, "rgba(0,20,100,0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.18, 0, Math.PI * 2);
    ctx.fill();

    // Globe rim
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(30,140,255,0.28)";
    ctx.lineWidth = 1.0;
    ctx.stroke();
  }

  function handleMouseDown(e) { isDragging.current = true; lastPos.current = [e.clientX, e.clientY]; }
  function handleMouseMove(e) {
    if (!isDragging.current) return;
    const dx = e.clientX - lastPos.current[0], dy = e.clientY - lastPos.current[1];
    rotationRef.current = [rotationRef.current[0] + dx * 0.35, Math.max(-75, Math.min(75, rotationRef.current[1] - dy * 0.28))];
    lastPos.current = [e.clientX, e.clientY];
  }
  function handleMouseUp() { isDragging.current = false; }

  function handleClick(e) {
    if (!d3Ref.current || !geoDataRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
    const my = (e.clientY - rect.top) * (canvas.height / rect.height);
    const proj = getProjection(canvas);
    const inv = proj.invert([mx, my]);
    if (!inv) return;
    let clicked = null;
    for (const feature of geoDataRef.current.features) {
      if (d3Ref.current.geoContains(feature, inv)) {
        const code = NUMERIC_TO_CODE[feature.id?.toString().padStart(3, "0")];
        if (code && allRisksRef.current[code]) { clicked = allRisksRef.current[code]; break; }
      }
    }
    if (clicked) onCountryClick(clicked);
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; starsRef.current = genStars(canvas.width, canvas.height); };
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  return (
    <canvas ref={canvasRef}
      style={{ width: "100%", height: "100%", cursor: "grab", display: "block", background: "#010204" }}
      onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp} onClick={handleClick}
    />
  );
}

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTicker, setActiveTicker] = useState("JPM");
  const [tab, setTab] = useState("globe");
  const [pulse, setPulse] = useState(false);
  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, content: null });
  const [selectedSignal, setSelectedSignal] = useState(AI_SIGNALS[0]);
  const [geoSelected, setGeoSelected] = useState(null);
  const [geoHistory, setGeoHistory] = useState([]);
  const [globeSelected, setGlobeSelected] = useState(null);
  const [globeHistory, setGlobeHistory] = useState([]);
  const [globeChartType, setGlobeChartType] = useState("bar");
  const [globeAsset, setGlobeAsset] = useState(null);

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/dashboard`);
      setDashboard(res.data);
      setLoading(false);
    } catch (e) { console.error(e); setLoading(false); }
  }, []);

  const fetchHistory = useCallback(async (ticker) => {
    try {
      const res = await axios.get(`${API}/api/market/history/${ticker}?days=60`);
      setHistory(res.data.data || []);
    } catch (e) { setHistory([]); }
  }, []);

  const fetchGeoHistory = useCallback(async (ticker) => {
    try {
      const res = await axios.get(`${API}/api/market/history/${ticker}?days=30`);
      setGeoHistory(res.data.data || []);
    } catch (e) { setGeoHistory([]); }
  }, []);

  useEffect(() => { fetchDashboard(); const i = setInterval(fetchDashboard, 60000); return () => clearInterval(i); }, [fetchDashboard]);
  useEffect(() => { fetchHistory(activeTicker); }, [activeTicker, fetchHistory]);
  useEffect(() => { const t = setInterval(() => setPulse(p => !p), 1500); return () => clearInterval(t); }, []);

  const handleGeoCountryClick = (risk) => {
    setGeoSelected(risk);
    const asset = COUNTRY_ASSET[risk.country] || { ticker: "GLD", label: "Gold" };
    fetchGeoHistory(asset.ticker);
  };

  const handleGlobeCountryClick = async (risk) => {
    // Pre-load data
    const asset = COUNTRY_ASSET[risk.country] || { ticker: "GLD", label: "Gold" };
    setGlobeAsset(asset);
    setGlobeSelected(risk);
    // Navigate to Geo Map tab and pre-select this country
    setGeoSelected(risk);
    setTab("map");
    try {
      const res = await axios.get(`${API}/api/market/history/${asset.ticker}?days=30`);
      const data = res.data.data || [];
      setGlobeHistory(data);
      setGeoHistory(data);
    } catch (e) { setGlobeHistory([]); setGeoHistory([]); }
  };

  if (loading) return (
    <div style={S.loader}>
      <div style={S.loaderBox}>
        <div style={S.loaderRing} />
        <div style={S.loaderTitle}>GEOFINANCE INTELLIGENCE</div>
        <div style={S.loaderSub}>Connecting to global data streams...</div>
      </div>
    </div>
  );

  const market = dashboard?.market || {};
  const geo = dashboard?.geopolitical || {};
  const newsData = dashboard?.news || {};
  const prices = market?.prices || {};
  const stress = market?.stress || {};
  const tension = geo?.tension || {};
  const allRisks = geo?.all_risks || {};
  const topRisks = geo?.top_risks || [];
  const recentNews = newsData?.recent || [];
  const keyTickers = ["JPM", "GS", "SPY", "GLD", "^VIX"];
  const getSentColor = (s) => s === "positive" ? "#00c853" : s === "negative" ? "#ff1744" : "#ffd600";

  const gti = tension.index || 0;
  const gtiColor = gti > 70 ? "#ff1744" : gti > 40 ? "#ff6d00" : "#ffd600";
  const gtiLabel = gti > 70 ? "CRITICAL" : gti > 40 ? "ELEVATED" : "MODERATE";

  return (
    <div style={S.app}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #0a0e1a; }
        ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 2px; }
        canvas { image-rendering: crisp-edges; }
      `}</style>
      <div style={S.bgGrid} />
      <div style={S.bgGlow} />

      {/* HEADER */}
      <header style={S.header}>
        <div style={S.logo}>
          <div style={S.logoIconWrap}>
            <span style={S.logoIcon}>◈</span>
          </div>
          <div>
            <div style={S.logoTitle}>GEOFINANCE INTELLIGENCE</div>
            <div style={S.logoSub}>GLOBAL RISK & MARKET ANALYTICS PLATFORM</div>
          </div>
        </div>

        {/* Center tabs - GeoTrade style */}
        <div style={S.centerTabs}>
          {[
            ["globe", "🌐  EARTH PULSE"],
            ["map", "🗺  GEO MAP"],
            ["signals", "⚡  AI SIGNALS"],
          ].map(([id, label]) => (
            <button key={id} style={{ ...S.centerTab, ...(tab === id ? S.centerTabActive : {}) }}
              onClick={() => setTab(id)}>{label}</button>
          ))}
        </div>

        <div style={S.headerRight}>
          <div style={S.live}>
            <div style={{ ...S.liveDot, opacity: pulse ? 1 : 0.2 }} />
            <span style={S.liveText}>LIVE</span>
          </div>
          <div style={S.gtiChip}>
            <span style={{ color: "#555", fontSize: 9 }}>GTI</span>
            <span style={{ color: gtiColor, fontSize: 13, fontWeight: "bold" }}>{gti.toFixed(1)}</span>
            <span style={{ ...S.gtiBadge, background: gtiColor + "22", color: gtiColor, border: `1px solid ${gtiColor}` }}>{gtiLabel}</span>
          </div>
          <div style={S.clock}>{new Date().toUTCString().slice(0, 25)} UTC</div>
        </div>
      </header>

      {/* KPI STRIP */}
      <div style={S.kpiStrip}>
        {keyTickers.map(t => {
          const d = prices[t]; if (!d) return null;
          const up = d.change_pct >= 0;
          return (
            <div key={t} style={{ ...S.kpiCard, borderColor: activeTicker === t ? "#00d4ff33" : "rgba(255,255,255,0.05)" }}
              onClick={() => setActiveTicker(t)}>
              <div style={S.kpiLabel}>{d.name}</div>
              <div style={S.kpiPrice}>${d.price.toLocaleString()}</div>
              <div style={{ ...S.kpiChange, color: up ? "#00c853" : "#ff1744" }}>{up ? "▲" : "▼"} {Math.abs(d.change_pct).toFixed(2)}%</div>
            </div>
          );
        })}
        <div style={{ ...S.kpiCard, borderColor: "rgba(255,140,0,0.15)" }}>
          <div style={S.kpiLabel}>MARKET STRESS</div>
          <div style={{ ...S.kpiPrice, color: stress.stress_index > 50 ? "#ff1744" : "#ffd600" }}>{stress.stress_index}/100</div>
          <div style={{ ...S.kpiChange, color: "#666" }}>{stress.level}</div>
        </div>
        <div style={{ ...S.kpiCard, borderColor: "rgba(255,50,50,0.15)" }}>
          <div style={S.kpiLabel}>GEO TENSION</div>
          <div style={{ ...S.kpiPrice, color: gtiColor }}>{tension.index}/100</div>
          <div style={{ ...S.kpiChange, color: "#666" }}>{tension.level}</div>
        </div>
      </div>

      {/* BOTTOM TICKER */}
      <div style={S.tickerBar}>
        {recentNews.slice(0, 5).map((n, i) => (
          <span key={i} style={S.tickerItem}>
            <span style={{ color: getSentColor(n.sentiment), marginRight: 4 }}>●</span>
            <span style={{ color: "#666" }}>{n.title?.slice(0, 60)}...</span>
            <span style={{ color: "#333", margin: "0 20px" }}>|</span>
          </span>
        ))}
      </div>

      <div style={S.main}>

        {/* ===== TAB 1: EARTH PULSE (3D Globe) ===== */}
        {tab === "globe" && (
          <div style={{ position: "relative", height: "calc(100vh - 185px)", background: "#020408" }}>

            {/* Full-screen globe */}
            <Globe3D allRisks={allRisks} onCountryClick={handleGlobeCountryClick} selectedCode={globeSelected?.country} />

            {/* Bottom center hint */}
            <div style={{ position: "absolute", bottom: 14, left: "50%", transform: "translateX(-50%)", fontSize: 9, color: "rgba(0,212,255,0.45)", letterSpacing: 2, pointerEvents: "none", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#00d4ff88", display: "inline-block" }} />
              CLICK ANY COUNTRY TO VIEW MARKET IMPACT  ›
            </div>

            {/* Bottom-left risk legend */}
            <div style={{ position: "absolute", bottom: 14, left: 14, display: "flex", flexDirection: "column", gap: 5 }}>
              <div style={{ fontSize: 8, color: "#333", letterSpacing: 2, marginBottom: 4 }}>RISK LEVEL</div>
              {[["CRITICAL 80+", "#d50000"], ["HIGH 50-80", "#ff6d00"], ["MEDIUM 25-50", "#ffd600"], ["LOW < 25", "#00c853"]].map(([l, c]) => (
                <div key={l} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: c, boxShadow: `0 0 6px ${c}66` }} />
                  <span style={{ fontSize: 8, color: "rgba(255,255,255,0.3)", letterSpacing: 1 }}>{l}</span>
                </div>
              ))}
            </div>

            {/* Floating SIGNALS panel — top right */}
            <div style={{ position: "absolute", top: 0, right: 0, width: 290, background: "rgba(4,8,18,0.94)", border: "1px solid rgba(0,212,255,0.15)", borderRadius: "0 0 0 10px", backdropFilter: "blur(16px)", padding: 16, maxHeight: "92%", overflowY: "auto" }}>
              {/* Panel header */}
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, paddingBottom: 10, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#00d4ff", display: "inline-block", boxShadow: "0 0 8px #00d4ff" }} />
                <span style={{ fontSize: 10, color: "#00d4ff", letterSpacing: 3, fontWeight: "bold" }}>SIGNALS</span>
              </div>

              {/* Featured signal */}
              {(() => {
                const sig = AI_SIGNALS[0];
                const d = prices["GLD"];
                const up = d?.change_pct >= 0;
                return (
                  <div style={{ marginBottom: 14, paddingBottom: 14, borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: "bold", color: "#fff" }}>{sig.ticker}</div>
                        <div style={{ fontSize: 9, color: "#555" }}>{sig.category}</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ ...S.signalBadge, background: "#00c85322", border: "1px solid #00c853", color: "#00c853", fontSize: 9, padding: "3px 10px", marginBottom: 4 }}>BUY</div>
                        <div style={{ fontSize: 13, fontWeight: "bold", color: "#fff" }}>${d?.price?.toFixed(2) || "—"}</div>
                        <div style={{ fontSize: 9, color: up ? "#00c853" : "#ff1744" }}>{up ? "▲" : "▼"}{Math.abs(d?.change_pct || 0).toFixed(2)}%</div>
                      </div>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontSize: 8, color: "#00c853" }}>Confidence: {sig.confidence}%</span>
                      <span style={{ fontSize: 8, color: "#ff6d00" }}>Uncertainty: {100-sig.confidence}%</span>
                    </div>
                    <div style={{ height: 3, background: "#ff174422", borderRadius: 2, marginBottom: 10, position: "relative" }}>
                      <div style={{ width: `${sig.confidence}%`, height: "100%", background: "linear-gradient(90deg,#00c853,#00d4ff)", borderRadius: 2 }} />
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 7 }}>
                      <span style={{ fontSize: 8, color: "#00d4ff", border: "1px solid rgba(0,212,255,0.3)", borderRadius: 3, padding: "2px 7px", letterSpacing: 1 }}>◈ AI ANALYSIS</span>
                    </div>
                    <div style={{ fontSize: 9, color: "#888", lineHeight: 1.6, marginBottom: 8 }}>Safe haven flows increasing due to elevated geopolitical stress.</div>
                    <div style={{ fontSize: 8, color: "#ff6d00", letterSpacing: 1, marginBottom: 5 }}>⚠ RISK FACTORS</div>
                    {sig.trigger.split("—").filter(Boolean).map((t, i) => (
                      <div key={i} style={{ fontSize: 8, color: "#ff6d0099", marginBottom: 3 }}>→ {t.trim()}</div>
                    ))}
                  </div>
                );
              })()}

              {/* All signals */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <span style={{ fontSize: 9, color: "#444", letterSpacing: 2 }}>ALL SIGNALS ({AI_SIGNALS.length})</span>
                <span style={{ fontSize: 9, color: "#00d4ff44" }}>⌄</span>
              </div>
              {AI_SIGNALS.map(sig => {
                const d = prices[sig.ticker] || prices["GLD"];
                return (
                  <div key={sig.ticker} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid rgba(255,255,255,0.04)", cursor: "pointer" }}
                    onClick={() => { setSelectedSignal(sig); setTab("signals"); }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontSize: 11, fontWeight: "bold", color: "#fff" }}>{sig.ticker}</span>
                        <span style={{ background: sig.color + "22", border: `1px solid ${sig.color}`, color: sig.color, fontSize: 8, padding: "1px 7px", borderRadius: 3, letterSpacing: 1 }}>{sig.signal}</span>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 10, color: sig.signal === "BUY" ? "#00c853" : sig.signal === "SELL" ? "#ff1744" : "#ffd600", fontWeight: "bold" }}>
                          {sig.signal === "SELL" ? "-" : "+"}{(sig.confidence * 0.03).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    <div style={{ fontSize: 9, color: "#444", marginBottom: 5 }}>{sig.category}</div>
                    <div style={{ height: 2, background: "rgba(255,255,255,0.06)", borderRadius: 1 }}>
                      <div style={{ width: `${sig.bullish}%`, height: "100%", background: sig.color, borderRadius: 1 }} />
                    </div>
                  </div>
                );
              })}
              <div style={{ fontSize: 9, color: "#00d4ff88", textAlign: "center", cursor: "pointer", paddingTop: 6, letterSpacing: 2 }}
                onClick={() => setTab("signals")}>VIEW ALL SIGNALS →</div>
            </div>
          </div>
        )}

        {/* ===== TAB 2: GEO MAP (flat map + candlestick) ===== */}
        {tab === "map" && (
          <div style={S.geoMapPage}>
            {/* Left: flat map */}
            <div style={S.geoMapLeft}>
              <div style={S.panelTitle}>GEOPOLITICAL RISK MAP — click country to view market impact</div>
              <div style={S.mapBox}>
                <ComposableMap
                  projection="geoMercator"
                  projectionConfig={{ scale: 130, center: [15, 15] }}
                  style={{ width: "100%", height: "100%", background: "#080d1a" }}>
                  <ZoomableGroup zoom={1}>
                    <Geographies geography={GEO_URL}>
                      {({ geographies }) =>
                        geographies.map(geo => {
                          const numId = geo.id?.toString().padStart(3, "0");
                          const code = NUMERIC_TO_CODE[numId];
                          const risk = code ? allRisks[code] : null;
                          const score = risk?.risk_score;
                          const fill = risk ? RISK_COLOR(score) : (code ? "#1e2d45" : "#0d1520");
                          const isSelected = geoSelected?.country === code;
                          return (
                            <Geography
                              key={geo.rsmKey}
                              geography={geo}
                              fill={isSelected ? "#00d4ff" : fill}
                              fillOpacity={risk ? 0.85 : 0.55}
                              stroke="#0a0f1e"
                              strokeWidth={0.5}
                              style={{
                                default: { outline: "none" },
                                hover: { outline: "none", fill: risk ? "#00d4ff" : fill, cursor: risk ? "pointer" : "default", fillOpacity: 1 },
                                pressed: { outline: "none" },
                              }}
                              onClick={() => { if (risk) handleGeoCountryClick(risk); }}
                              onMouseEnter={(e) => {
                                if (!risk) return;
                                setTooltip({ show: true, x: e.clientX, y: e.clientY, content: { code, score, level: risk.level, region: risk.region } });
                              }}
                              onMouseLeave={() => setTooltip({ show: false, x: 0, y: 0, content: null })}
                            />
                          );
                        })
                      }
                    </Geographies>
                  </ZoomableGroup>
                </ComposableMap>
                {tooltip.show && tooltip.content && (
                  <div style={{ ...S.mapTooltip, left: tooltip.x + 12, top: tooltip.y - 40 }}>
                    <span style={{ color: "#00d4ff", fontWeight: "bold" }}>{tooltip.content.code}</span>
                    <span style={{ color: RISK_COLOR(tooltip.content.score), marginLeft: 8 }}>
                      {tooltip.content.score} — {tooltip.content.level}
                    </span>
                    <span style={{ color: "#555", marginLeft: 8, fontSize: 10 }}>{tooltip.content.region}</span>
                  </div>
                )}
              </div>
              <div style={S.legend}>
                {[["< 25 LOW", "#00c853"], ["25-50 MODERATE", "#ffd600"], ["50-75 HIGH", "#ff6d00"], ["75+ CRITICAL", "#d50000"]].map(([l, c]) => (
                  <div key={l} style={S.legendItem}>
                    <div style={{ ...S.legendDot, background: c }} />
                    <span style={{ color: "#555", fontSize: 9 }}>{l}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: asset chart */}
            <div style={S.geoMapRight}>
              {geoSelected ? (
                <>
                  <div style={S.geoChartHeader}>
                    <div>
                      <div style={{ fontSize: 18, fontWeight: "bold", color: "#fff", marginBottom: 4 }}>
                        {geoSelected.country}
                        <span style={{ fontSize: 11, color: "#555", marginLeft: 10 }}>{geoSelected.region}</span>
                      </div>
                      <div style={{ display: "flex", gap: 12 }}>
                        {(() => {
                          const asset = COUNTRY_ASSET[geoSelected.country] || { ticker: "GLD", label: "Gold" };
                          const d = prices[asset.ticker];
                          const up = d?.change_pct >= 0;
                          return (
                            <>
                              <span style={{ fontSize: 13, fontWeight: "bold", color: "#00d4ff" }}>{asset.ticker}</span>
                              {d && <span style={{ fontSize: 13, color: "#fff" }}>${d.price?.toFixed(2)}</span>}
                              {d && <span style={{ fontSize: 12, color: up ? "#00c853" : "#ff1744" }}>{up ? "▲" : "▼"} {Math.abs(d.change_pct).toFixed(2)}%</span>}
                              <span style={{ fontSize: 11, color: "#555" }}>{asset.label}</span>
                            </>
                          );
                        })()}
                      </div>
                    </div>
                    <div style={{ ...S.cBadge, background: RISK_BG(geoSelected.risk_score), border: `1px solid ${RISK_COLOR(geoSelected.risk_score)}`, color: RISK_COLOR(geoSelected.risk_score), fontSize: 11, padding: "6px 12px" }}>
                      RISK {geoSelected.risk_score}
                    </div>
                  </div>

                  <div style={{ ...S.panelTitle, marginTop: 16 }}>SELECT ASSET TO MONITOR</div>
                  <div style={{ display: "flex", gap: 6, marginBottom: 16 }}>
                    {["GLD", "USO", "SPY", "EEM"].map(t => {
                      const d = prices[t]; if (!d) return null;
                      const up = d.change_pct >= 0;
                      return (
                        <div key={t} style={{ ...S.assetChip, borderColor: (COUNTRY_ASSET[geoSelected.country]?.ticker === t) ? "#00d4ff" : "rgba(255,255,255,0.08)" }}
                          onClick={() => fetchGeoHistory(t)}>
                          <div style={{ fontSize: 10, fontWeight: "bold", color: "#00d4ff" }}>{t}</div>
                          <div style={{ fontSize: 10, color: "#fff" }}>${d.price?.toFixed(2)}</div>
                          <div style={{ fontSize: 9, color: up ? "#00c853" : "#ff1744" }}>{up ? "▲" : "▼"}{Math.abs(d.change_pct).toFixed(2)}%</div>
                        </div>
                      );
                    })}
                  </div>

                  <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8, padding: 16 }}>
                    <div style={S.panelTitle}>30-DAY PRICE HISTORY</div>
                    <CandlestickChart data={geoHistory} />
                  </div>

                  <div style={{ marginTop: 14, background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8, padding: 14 }}>
                    <div style={S.panelTitle}>SECTOR EXPOSURE</div>
                    {[
                      ["Energy", geoSelected.risk_score > 50 ? 75 : 30, "#ff6d00"],
                      ["Defense", geoSelected.risk_score > 65 ? 85 : 25, "#00d4ff"],
                      ["Finance", geoSelected.risk_score > 40 ? 45 : 20, "#ffd600"],
                    ].map(([name, pct, color]) => (
                      <div key={name} style={{ marginBottom: 10 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                          <span style={{ fontSize: 10, color: "#666" }}>{name}</span>
                          <span style={{ fontSize: 10, color }}>{pct}%</span>
                        </div>
                        <div style={{ height: 3, background: "rgba(255,255,255,0.07)", borderRadius: 2 }}>
                          <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 2 }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div style={{ ...S.selectPrompt, height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ fontSize: 36, marginBottom: 12 }}>🗺</div>
                  <div style={{ color: "#555", fontSize: 11 }}>Click any highlighted country on the map</div>
                  <div style={{ color: "#333", fontSize: 10, marginTop: 4 }}>to view market impact & asset chart</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===== TAB 3: AI SIGNALS ===== */}
        {tab === "signals" && (
          <div style={S.signalsPage}>
            {/* Left: signal list */}
            <div style={S.signalList}>
              <div style={S.panelTitle}>AI SIGNAL ENGINE — {AI_SIGNALS.length} ACTIVE SIGNALS</div>
              <input placeholder="🔍  Search asset..." style={S.searchBox} readOnly />
              {["All", "Commodities", "Equity", "Forex", "Crypto"].map(cat => (
                <span key={cat} style={S.filterChip}>{cat}</span>
              ))}
              <div style={{ marginTop: 12 }}>
                {AI_SIGNALS.map(sig => (
                  <div key={sig.ticker} style={{ ...S.signalCard, borderColor: selectedSignal?.ticker === sig.ticker ? sig.color : "rgba(255,255,255,0.06)" }}
                    onClick={() => setSelectedSignal(sig)}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <div>
                        <span style={{ fontSize: 13, fontWeight: "bold", color: "#fff" }}>{sig.ticker}</span>
                        <span style={{ fontSize: 10, color: "#555", marginLeft: 8 }}>{sig.name}</span>
                      </div>
                      <div style={{ ...S.signalBadge, background: sig.color + "22", border: `1px solid ${sig.color}`, color: sig.color }}>{sig.signal}</div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                          <span style={{ fontSize: 8, color: "#00c853" }}>BULL</span>
                          <span style={{ fontSize: 8, color: "#ff1744" }}>BEAR</span>
                        </div>
                        <div style={{ height: 4, background: "#ff174422", borderRadius: 2, position: "relative" }}>
                          <div style={{ width: `${sig.bullish}%`, height: "100%", background: "#00c853", borderRadius: 2 }} />
                        </div>
                      </div>
                      <span style={{ fontSize: 11, fontWeight: "bold", color: sig.color }}>{sig.confidence}%</span>
                    </div>
                    <div style={{ fontSize: 9, color: "#555" }}>{sig.category}</div>
                    <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
                      <span style={{ ...S.miniChip, borderColor: "rgba(0,212,255,0.3)", color: "#00d4ff" }}>{sig.volatility}</span>
                      <span style={{ ...S.miniChip, borderColor: "rgba(255,255,255,0.1)", color: "#666" }}>{sig.timeframe}</span>
                    </div>
                    <div style={{ fontSize: 9, color: "#444", marginTop: 6, lineHeight: 1.4 }}>
                      {sig.trigger}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: signal detail */}
            {selectedSignal && (
              <div style={S.signalDetail}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, paddingBottom: 16, borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                  <div>
                    <div style={{ fontSize: 22, fontWeight: "bold", color: "#fff" }}>{selectedSignal.ticker}</div>
                    <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>{selectedSignal.name} · {selectedSignal.category}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ ...S.signalBadge, background: selectedSignal.color + "22", border: `1px solid ${selectedSignal.color}`, color: selectedSignal.color, fontSize: 14, padding: "6px 16px" }}>
                      {selectedSignal.signal}
                    </div>
                    <div style={{ fontSize: 20, fontWeight: "bold", color: selectedSignal.color, marginTop: 6 }}>{selectedSignal.confidence}%</div>
                    <div style={{ fontSize: 9, color: "#555" }}>confidence</div>
                  </div>
                </div>

                {/* Bullish / Bearish bars */}
                <div style={{ marginBottom: 20 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 10, color: "#00c853" }}>Bullish Strength</span>
                    <span style={{ fontSize: 10, color: "#ff1744" }}>Bearish Strength</span>
                  </div>
                  <div style={{ height: 6, background: "#ff174422", borderRadius: 3, position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", left: 0, top: 0, height: "100%", width: `${selectedSignal.bullish}%`, background: "linear-gradient(90deg,#00c85388,#00c853)", borderRadius: 3 }} />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                    <span style={{ fontSize: 9, color: "#00c853" }}>{selectedSignal.bullish}%</span>
                    <span style={{ fontSize: 9, color: "#ff1744" }}>{selectedSignal.bearish}%</span>
                  </div>
                </div>

                {/* Volatility + timeframe chips */}
                <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
                  <span style={{ ...S.detailChip, borderColor: "rgba(0,212,255,0.4)", color: "#00d4ff" }}>{selectedSignal.volatility} VOLATILITY</span>
                  <span style={{ ...S.detailChip, borderColor: "rgba(255,255,255,0.15)", color: "#888" }}>{selectedSignal.timeframe}</span>
                  <span style={{ ...S.detailChip, borderColor: "rgba(255,214,0,0.3)", color: "#ffd600" }}>GLOBAL</span>
                </div>

                {/* Trigger */}
                <div style={{ ...S.triggerBox, borderColor: "rgba(255,107,0,0.3)" }}>
                  <div style={{ fontSize: 9, color: "#ff6d00", letterSpacing: 2, marginBottom: 6 }}>⚡ TRIGGERING EVENT</div>
                  <div style={{ fontSize: 12, color: "#ddd" }}>{selectedSignal.trigger}</div>
                </div>

                {/* Trade Setup tabs */}
                <div style={{ display: "flex", gap: 0, marginBottom: 16, borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                  {["TRADE SETUP", "AI REASONING", "TIMELINE", "RELIABILITY"].map((t, i) => (
                    <button key={t} style={{ ...S.detailTab, ...(i === 0 ? S.detailTabActive : {}) }}>{t}</button>
                  ))}
                </div>

                {/* Trade setup grid */}
                <div style={S.tradeGrid}>
                  {[
                    ["CURRENT PRICE", `$${selectedSignal.entry.toLocaleString()}`],
                    ["ENTRY", `$${selectedSignal.entry.toLocaleString()}`],
                    ["STOP LOSS", `$${selectedSignal.stop.toLocaleString()}`],
                    ["TARGET", `$${selectedSignal.target.toLocaleString()}`],
                    ["RISK/REWARD", selectedSignal.riskReward],
                    ["ATR (DAILY)", selectedSignal.winRate],
                    ["MAX P&L", selectedSignal.maxPnL],
                  ].map(([k, v]) => (
                    <div key={k} style={S.tradeCell}>
                      <div style={{ fontSize: 9, color: "#555", letterSpacing: 1, marginBottom: 4 }}>{k}</div>
                      <div style={{ fontSize: 16, fontWeight: "bold", color: k === "STOP LOSS" ? "#ff1744" : k === "TARGET" ? "#00c853" : "#fff" }}>{v}</div>
                    </div>
                  ))}
                </div>

                {/* Win rate bar */}
                <div style={{ marginTop: 16, background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 6, padding: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 9, color: "#555" }}>WIN vs XAUUSD</span>
                    <span style={{ fontSize: 9, color: "#00c853" }}>+85.000%</span>
                  </div>
                  <div style={{ height: 4, background: "rgba(255,255,255,0.07)", borderRadius: 2 }}>
                    <div style={{ width: "85%", height: "100%", background: "linear-gradient(90deg,#00c853,#00d4ff)", borderRadius: 2 }} />
                  </div>
                </div>

                <div style={{ marginTop: 14, fontSize: 9, color: "#333", lineHeight: 1.6 }}>
                  ⓘ Educational purposes only. Not financial advice. Always perform your own due diligence.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const S = {
  app: { minHeight: "100vh", background: "#060912", fontFamily: "'Courier New',monospace", color: "#e0e0e0", position: "relative", overflow: "hidden", display: "flex", flexDirection: "column" },
  bgGrid: { position: "fixed", inset: 0, zIndex: 0, backgroundImage: `linear-gradient(rgba(0,212,255,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.025) 1px,transparent 1px)`, backgroundSize: "40px 40px", pointerEvents: "none" },
  bgGlow: { position: "fixed", top: "-20%", left: "30%", width: "40%", height: "60%", background: "radial-gradient(ellipse,rgba(0,100,255,0.05) 0%,transparent 70%)", pointerEvents: "none", zIndex: 0 },
  loader: { minHeight: "100vh", background: "#060912", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Courier New',monospace" },
  loaderBox: { textAlign: "center" },
  loaderRing: { width: 56, height: 56, margin: "0 auto 20px", border: "2px solid rgba(0,212,255,0.15)", borderTop: "2px solid #00d4ff", borderRadius: "50%", animation: "spin 1s linear infinite" },
  loaderTitle: { color: "#00d4ff", fontSize: 13, letterSpacing: 4, marginBottom: 8 },
  loaderSub: { color: "#444", fontSize: 11 },
  header: { position: "relative", zIndex: 10, display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 24px", borderBottom: "1px solid rgba(0,212,255,0.1)", background: "rgba(6,9,18,0.97)", backdropFilter: "blur(10px)" },
  logo: { display: "flex", alignItems: "center", gap: 12 },
  logoIconWrap: { width: 36, height: 36, borderRadius: "50%", border: "1px solid rgba(0,212,255,0.3)", display: "flex", alignItems: "center", justifyContent: "center" },
  logoIcon: { fontSize: 18, color: "#00d4ff" },
  logoTitle: { fontSize: 13, fontWeight: "bold", color: "#00d4ff", letterSpacing: 3 },
  logoSub: { fontSize: 8, color: "#333", letterSpacing: 2, marginTop: 2 },
  centerTabs: { display: "flex", gap: 0, background: "rgba(0,0,0,0.4)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 6, overflow: "hidden" },
  centerTab: { padding: "8px 20px", background: "transparent", border: "none", borderRight: "1px solid rgba(255,255,255,0.06)", color: "#555", cursor: "pointer", fontSize: 10, letterSpacing: 2, transition: "all 0.2s" },
  centerTabActive: { color: "#00d4ff", background: "rgba(0,212,255,0.08)" },
  headerRight: { display: "flex", alignItems: "center", gap: 16 },
  live: { display: "flex", alignItems: "center", gap: 6 },
  liveDot: { width: 7, height: 7, borderRadius: "50%", background: "#ff1744", transition: "opacity 0.5s" },
  liveText: { fontSize: 9, color: "#ff1744", letterSpacing: 2 },
  gtiChip: { display: "flex", alignItems: "center", gap: 6, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 6, padding: "4px 10px" },
  gtiBadge: { padding: "2px 6px", borderRadius: 3, fontSize: 8, letterSpacing: 1, fontWeight: "bold" },
  clock: { fontSize: 9, color: "#333" },
  kpiStrip: { position: "relative", zIndex: 10, display: "flex", gap: 0, background: "rgba(0,0,0,0.7)", borderBottom: "1px solid rgba(255,255,255,0.04)", overflowX: "auto", flexShrink: 0 },
  kpiCard: { padding: "8px 16px", minWidth: 115, borderRight: "1px solid rgba(255,255,255,0.04)", border: "1px solid transparent", background: "transparent", cursor: "pointer", transition: "all 0.2s" },
  kpiLabel: { fontSize: 8, color: "#444", letterSpacing: 2, marginBottom: 2 },
  kpiPrice: { fontSize: 13, fontWeight: "bold", color: "#fff", marginBottom: 1 },
  kpiChange: { fontSize: 9 },
  tickerBar: { position: "relative", zIndex: 10, background: "rgba(0,0,0,0.5)", borderBottom: "1px solid rgba(255,255,255,0.03)", padding: "4px 24px", display: "flex", overflowX: "hidden", flexShrink: 0 },
  tickerItem: { fontSize: 9, whiteSpace: "nowrap", display: "flex", alignItems: "center" },
  main: { position: "relative", zIndex: 10, padding: "14px 18px", flex: 1, overflow: "hidden" },
  panelTitle: { fontSize: 9, color: "#555", letterSpacing: 3, marginBottom: 10, textTransform: "uppercase" },

  // Globe tab
  globePage: { display: "grid", gridTemplateColumns: "1fr 300px", gap: 16, height: "calc(100vh - 190px)" },
  globeWrap: { display: "flex", flexDirection: "column" },
  globeBox: { flex: 1, background: "#060912", borderRadius: 10, border: "1px solid rgba(0,212,255,0.1)", overflow: "hidden", position: "relative", minHeight: 0 },
  globeHint: { position: "absolute", bottom: 10, left: "50%", transform: "translateX(-50%)", fontSize: 9, color: "#333", letterSpacing: 2, pointerEvents: "none" },
  globeLegend: { display: "flex", gap: 16, marginTop: 10, alignItems: "center" },
  globeRight: { display: "flex", flexDirection: "column", overflowY: "auto" },

  // Geo map tab
  geoMapPage: { display: "grid", gridTemplateColumns: "1fr 420px", gap: 16, height: "calc(100vh - 190px)" },
  geoMapLeft: { display: "flex", flexDirection: "column" },
  geoMapRight: { overflowY: "auto", paddingLeft: 4 },
  geoChartHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8, padding: 14 },
  assetChip: { flex: 1, background: "rgba(255,255,255,0.02)", border: "1px solid", borderRadius: 6, padding: "8px 10px", cursor: "pointer", textAlign: "center" },

  // Signals tab
  signalsPage: { display: "grid", gridTemplateColumns: "340px 1fr", gap: 16, height: "calc(100vh - 190px)" },
  signalList: { overflowY: "auto" },
  searchBox: { width: "100%", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 6, padding: "8px 12px", color: "#555", fontSize: 10, marginBottom: 10, boxSizing: "border-box", outline: "none" },
  filterChip: { display: "inline-block", padding: "3px 10px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 20, fontSize: 9, color: "#555", marginRight: 6, marginBottom: 10, cursor: "pointer" },
  signalCard: { background: "rgba(255,255,255,0.02)", border: "1px solid", borderRadius: 8, padding: 14, marginBottom: 10, cursor: "pointer", transition: "border-color 0.2s" },
  signalBadge: { padding: "3px 10px", borderRadius: 4, fontSize: 10, fontWeight: "bold", letterSpacing: 2 },
  miniChip: { padding: "2px 7px", border: "1px solid", borderRadius: 3, fontSize: 8, letterSpacing: 1 },
  signalDetail: { overflowY: "auto", background: "rgba(255,255,255,0.01)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 10, padding: 24 },
  triggerBox: { border: "1px solid", borderRadius: 6, padding: 14, marginBottom: 20, background: "rgba(255,107,0,0.04)" },
  detailChip: { padding: "4px 12px", border: "1px solid", borderRadius: 20, fontSize: 9, letterSpacing: 1 },
  detailTab: { padding: "8px 14px", background: "transparent", border: "none", borderBottom: "2px solid transparent", color: "#444", cursor: "pointer", fontSize: 9, letterSpacing: 1 },
  detailTabActive: { color: "#00d4ff", borderBottomColor: "#00d4ff" },
  tradeGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
  tradeCell: { background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 6, padding: "12px 14px" },

  // Shared
  mapBox: { flex: 1, position: "relative", background: "#080d1a", borderRadius: 8, border: "1px solid rgba(0,212,255,0.1)", overflow: "hidden", minHeight: 0, minHeight: 400 },
  mapTooltip: { position: "fixed", background: "#0a0e1a", border: "1px solid rgba(0,212,255,0.3)", borderRadius: 6, padding: "6px 12px", fontSize: 11, pointerEvents: "none", zIndex: 1000, whiteSpace: "nowrap" },
  legend: { display: "flex", alignItems: "center", gap: 16, marginTop: 10 },
  legendItem: { display: "flex", alignItems: "center", gap: 5 },
  legendDot: { width: 8, height: 8, borderRadius: "50%" },
  countryCard: { background: "rgba(255,255,255,0.02)", border: "1px solid", borderRadius: 8, padding: 14 },
  cHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10, paddingBottom: 10, borderBottom: "1px solid rgba(255,255,255,0.06)" },
  cCode: { fontSize: 20, fontWeight: "bold", color: "#fff" },
  cBadge: { padding: "3px 8px", borderRadius: 4, fontSize: 9, letterSpacing: 2 },
  cScoreWrap: { textAlign: "center", margin: "10px 0" },
  cScore: { fontSize: 42, fontWeight: "bold", lineHeight: 1 },
  cScoreLbl: { fontSize: 8, color: "#555", letterSpacing: 2, marginTop: 2 },
  cBar: { height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, marginBottom: 10, overflow: "hidden" },
  cBarFill: { height: "100%", borderRadius: 2, transition: "width 0.5s" },
  cStats: { display: "flex", flexDirection: "column", gap: 5 },
  cStat: { display: "flex", justifyContent: "space-between" },
  cStatK: { fontSize: 10, color: "#555" },
  cStatV: { fontSize: 10, color: "#aaa" },
  factors: { marginTop: 10, paddingTop: 10, borderTop: "1px solid rgba(255,255,255,0.05)" },
  factorTitle: { fontSize: 9, color: "#ff6d00", letterSpacing: 2, marginBottom: 6 },
  factorItem: { fontSize: 10, color: "#ff6d00", marginBottom: 3 },
  selectPrompt: { background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 8, padding: 24, textAlign: "center" },
  topPanel: { background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 8, padding: 14 },
  riskRow: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8, cursor: "pointer" },
  riskCode: { fontSize: 10, fontWeight: "bold", width: 28 },
  miniBar: { flex: 1, height: 3, background: "rgba(255,255,255,0.07)", borderRadius: 2, overflow: "hidden" },
  miniBarFill: { height: "100%", borderRadius: 2 },
  riskNum: { fontSize: 10, width: 24, textAlign: "right" },
  newsCard: { background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 6, padding: 10, marginBottom: 8, flexShrink: 0 },
  newsTop: { display: "flex", alignItems: "center", gap: 8, marginBottom: 6 },
  sentTag: { padding: "2px 6px", borderRadius: 3, fontSize: 8, letterSpacing: 1, whiteSpace: "nowrap" },
  newsSource: { fontSize: 8, color: "#444" },
  newsTitle: { fontSize: 10, color: "#ccc", lineHeight: 1.5 },
  eTag: { fontSize: 9, padding: "2px 5px", background: "rgba(0,212,255,0.1)", border: "1px solid rgba(0,212,255,0.2)", borderRadius: 3, color: "#00d4ff" },
};