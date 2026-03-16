import { useState, useRef, useCallback, useEffect } from "react";

// ─── Constants ───────────────────────────────────────────────────────────────

const DOMAIN_META = {
  "INFORMATION-TECHNOLOGY": { label: "Information Technology", color: "#00D4FF", glow: "rgba(0,212,255,0.10)" },
  "TEACHER":                { label: "Education",              color: "#7CFC00", glow: "rgba(124,252,0,0.10)" },
  "HEALTHCARE":             { label: "Healthcare",             color: "#FF6EC7", glow: "rgba(255,110,199,0.10)" },
  "FINANCE":                { label: "Finance",                color: "#FFD700", glow: "rgba(255,215,0,0.10)" },
  "ENGINEERING":            { label: "Engineering",            color: "#FF7F50", glow: "rgba(255,127,80,0.10)" },
  "DESIGNER":               { label: "Design",                 color: "#DA70D6", glow: "rgba(218,112,214,0.10)" },
  "SALES":                  { label: "Sales",                  color: "#00FF7F", glow: "rgba(0,255,127,0.10)" },
  "HR":                     { label: "Human Resources",        color: "#FF6EC7", glow: "rgba(255,110,199,0.10)" },
  "CHEF":                   { label: "Culinary",               color: "#FF4500", glow: "rgba(255,69,0,0.10)" },
  "FITNESS":                { label: "Fitness",                color: "#7CFC00", glow: "rgba(124,252,0,0.10)" },
  "CONSULTANT":             { label: "Consulting",             color: "#00D4FF", glow: "rgba(0,212,255,0.10)" },
  "CONSTRUCTION":           { label: "Construction",           color: "#FFD700", glow: "rgba(255,215,0,0.10)" },
  "DIGITAL-MEDIA":          { label: "Digital Media",          color: "#DA70D6", glow: "rgba(218,112,214,0.10)" },
  "PUBLIC-RELATIONS":       { label: "Public Relations",       color: "#FF7F50", glow: "rgba(255,127,80,0.10)" },
  "MARKETING":              { label: "Marketing",              color: "#00FF7F", glow: "rgba(0,255,127,0.10)" },
};

const SITE_COLORS = {
  "Google Jobs":   "#4285F4",
  "Indeed":        "#2164F3",
  "Naukri":        "#FF7555",
  "Internshala":   "#00ADEF",
  "Apna":          "#7C4DFF",
  "Shine":         "#FF6B35",
  "TimesJobs":     "#E63946",
  "Glassdoor":     "#0CAA41",
  "Freshersworld": "#F5A623",
  "Foundit":       "#E91E8C",
};

const LOADING_STEPS = [
  "Extracting text from PDF",
  "Detecting domain with NLP",
  "Running prediction model",
  "Scoring skill matches",
  "Building job search links",
];

// ─── Sub-components ──────────────────────────────────────────────────────────

function ConfidenceRing({ value, color, size = 64 }) {
  const r    = size / 2 - 5;
  const circ = 2 * Math.PI * r;
  const dash = Math.min(value, 100) / 100 * circ;
  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4"/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="4"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{ transition: "stroke-dasharray 1.1s cubic-bezier(.4,0,.2,1)" }}/>
      </svg>
      <div style={{ position:"absolute", inset:0, display:"flex", alignItems:"center", justifyContent:"center" }}>
        <span style={{ fontSize: size > 56 ? 11 : 10, fontWeight: 700, color: "#fff" }}>
          {value.toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

function SkillTag({ skill, color, delay = 0 }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "4px 12px", borderRadius: 99, fontSize: 12, fontWeight: 500,
      background: `${color}14`, border: `1px solid ${color}33`, color,
      animation: `fadeUp 0.35s ease ${delay}s both`, whiteSpace: "nowrap"
    }}>
      <span style={{ width: 5, height: 5, borderRadius: "50%", background: color, flexShrink: 0 }}/>
      {skill}
    </span>
  );
}

function JobLinkRow({ name, url, index, accent }) {
  const [hov, setHov] = useState(false);
  const bg = SITE_COLORS[name] || "#555";
  const initial = name.charAt(0);
  return (
    <a href={url} target="_blank" rel="noopener noreferrer"
      onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
      style={{
        display: "flex", alignItems: "center", gap: 12, padding: "12px 14px",
        borderRadius: 12, textDecoration: "none",
        background: hov ? "rgba(255,255,255,0.055)" : "rgba(255,255,255,0.02)",
        border: `1px solid ${hov ? "rgba(255,255,255,0.12)" : "rgba(255,255,255,0.055)"}`,
        transition: "all 0.16s ease",
        animation: `fadeUp 0.35s ease ${index * 0.055}s both`
      }}>
      <div style={{
        width: 32, height: 32, borderRadius: 9, flexShrink: 0,
        background: bg, display: "flex", alignItems: "center",
        justifyContent: "center", fontSize: 13, fontWeight: 700, color: "#fff",
        boxShadow: hov ? `0 0 12px ${bg}70` : "none", transition: "box-shadow 0.2s"
      }}>{initial}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ margin: 0, fontSize: 13, fontWeight: 500, color: "#fff" }}>{name}</p>
        <p style={{ margin: "2px 0 0", fontSize: 11, color: "rgba(255,255,255,0.28)",
          overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {url.replace("https://", "").split("?")[0]}
        </p>
      </div>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
        stroke={hov ? accent : "rgba(255,255,255,0.18)"} strokeWidth="2"
        style={{ transition: "stroke 0.18s", flexShrink: 0 }}>
        <path d="M7 17L17 7M7 7h10v10"/>
      </svg>
    </a>
  );
}

function ScoreBar({ label, value, color }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
        <span style={{ fontSize: 12, color: "rgba(255,255,255,0.45)" }}>{label}</span>
        <span style={{ fontSize: 12, fontWeight: 600, color, fontFamily: "monospace" }}>
          {value.toFixed(1)}%
        </span>
      </div>
      <div style={{ height: 4, borderRadius: 99, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
        <div style={{
          height: "100%", borderRadius: 99, background: color,
          width: `${Math.min(value, 100)}%`,
          transition: "width 1.1s cubic-bezier(.4,0,.2,1)",
          boxShadow: `0 0 6px ${color}80`
        }}/>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function ResumeAnalyzer() {
  const [file, setFile]         = useState(null);
  const [dragging, setDragging] = useState(false);
  const [step, setStep]         = useState("upload");
  const [loadStep, setLoadStep] = useState(0);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const [showAll, setShowAll]   = useState(false);
  const inputRef = useRef();

  useEffect(() => {
    if (step !== "analyzing") return;
    let i = 0;
    const t = setInterval(() => {
      i++;
      if (i < LOADING_STEPS.length) setLoadStep(i);
      else clearInterval(t);
    }, 700);
    return () => clearInterval(t);
  }, [step]);

  const handleFile = useCallback((f) => {
    if (!f) return;
    if (f.type !== "application/pdf") { setError("PDF files only."); return; }
    setFile(f); setError(null);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }, [handleFile]);

  const analyze = async () => {
    if (!file) return;
    setStep("analyzing"); setLoadStep(0); setError(null); setShowAll(false);
    const fd = new FormData();
    fd.append("resume", file);
    try {
      // Uses CRA proxy — no hardcoded localhost needed
      const res  = await fetch("/analyze", { method: "POST", body: fd });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data); setStep("result");
    } catch (err) {
      // Fallback: try direct if proxy not configured
      try {
        const fd2  = new FormData(); fd2.append("resume", file);
        const res2 = await fetch("http://localhost:5000/analyze", { method: "POST", body: fd2 });
        const data2 = await res2.json();
        if (data2.error) throw new Error(data2.error);
        setResult(data2); setStep("result");
      } catch {
        setError("Cannot connect to Flask server. Make sure app.py is running:\n  cd Backend\n  python app.py");
        setStep("upload");
      }
    }
  };

  const reset = () => {
    setFile(null); setResult(null); setError(null);
    setStep("upload"); setShowAll(false);
  };

  const meta   = result ? (DOMAIN_META[result.domain] || DOMAIN_META["INFORMATION-TECHNOLOGY"]) : null;
  const accent = meta?.color || "#00D4FF";
  const top5   = result?.top5 || [];
  const links  = result?.links || [];
  const skills = result?.skills || [];

  // Show top 3 roles by default, all 5 if expanded
  const visibleRoles = showAll ? top5 : top5.slice(0, 3);

  return (
    <div style={{ minHeight: "100vh", background: "#07090E", fontFamily: "'Inter', -apple-system, sans-serif", color: "#fff" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes fadeUp  { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
        @keyframes spin    { to{transform:rotate(360deg)} }
        @keyframes pulse   { 0%,100%{opacity:1} 50%{opacity:0.2} }
        @keyframes scanline{ 0%{transform:translateY(-120%)} 100%{transform:translateY(600%)} }
        @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
        ::-webkit-scrollbar{width:4px}
        ::-webkit-scrollbar-track{background:#07090E}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:99px}
        a { text-decoration: none; }
      `}</style>

      {/* Grid background */}
      <div style={{
        position:"fixed", inset:0, pointerEvents:"none", zIndex:0,
        backgroundImage:"linear-gradient(rgba(255,255,255,0.022) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.022) 1px,transparent 1px)",
        backgroundSize:"50px 50px"
      }}/>
      <div style={{
        position:"fixed", top:"-10%", left:"50%", transform:"translateX(-50%)",
        width:700, height:500, borderRadius:"50%", pointerEvents:"none", zIndex:0,
        background:"radial-gradient(circle, rgba(0,212,255,0.035) 0%, transparent 65%)"
      }}/>

      <div style={{ position:"relative", zIndex:1, maxWidth:680, margin:"0 auto", padding:"52px 20px 100px" }}>

        {/* ── HEADER ── */}
        <div style={{ marginBottom: 52, animation: "fadeUp 0.6s ease both" }}>
          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:16 }}>
            <span style={{
              width:7, height:7, borderRadius:"50%", background:"#00D4FF",
              boxShadow:"0 0 10px #00D4FF", display:"inline-block",
              animation:"pulse 2.2s ease infinite"
            }}/>
            <span style={{ fontSize:11, color:"rgba(255,255,255,0.32)", letterSpacing:"0.16em", textTransform:"uppercase" }}>
              AI Resume Intelligence v2
            </span>
          </div>
          <h1 style={{
            fontSize:"clamp(38px,7vw,56px)", fontWeight:700, lineHeight:1.06,
            letterSpacing:"-0.025em", marginBottom:14,
            background:"linear-gradient(155deg, #fff 25%, rgba(255,255,255,0.35))",
            WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text"
          }}>
            Resume<br/>Analyzer
          </h1>
          <p style={{ fontSize:15, color:"rgba(255,255,255,0.36)", lineHeight:1.8, maxWidth:430 }}>
            Upload your resume — AI detects your domain, predicts top 5 job roles with confidence scores,
            and surfaces openings across 10 job platforms.
          </p>
        </div>

        {/* ── UPLOAD SCREEN ── */}
        {step === "upload" && (
          <div style={{ animation:"fadeUp 0.5s ease 0.1s both" }}>

            {/* Drop Zone */}
            <div
              onDragOver={e=>{e.preventDefault();setDragging(true)}}
              onDragLeave={()=>setDragging(false)}
              onDrop={onDrop}
              onClick={()=>inputRef.current?.click()}
              style={{
                position:"relative", overflow:"hidden",
                border:`1px solid ${dragging?"#00D4FF":file?"#7CFC00":"rgba(255,255,255,0.085)"}`,
                borderRadius:20, padding:"52px 32px", textAlign:"center", cursor:"pointer",
                background: dragging?"rgba(0,212,255,0.04)":file?"rgba(124,252,0,0.03)":"rgba(255,255,255,0.016)",
                boxShadow: dragging?"0 0 52px rgba(0,212,255,0.09)":file?"0 0 52px rgba(124,252,0,0.07)":"none",
                transition:"all 0.22s ease"
              }}
            >
              {dragging && (
                <div style={{
                  position:"absolute",left:0,right:0,height:2,top:0,
                  background:"linear-gradient(90deg,transparent,#00D4FF,transparent)",
                  animation:"scanline 1s ease infinite"
                }}/>
              )}
              <input ref={inputRef} type="file" accept=".pdf" style={{display:"none"}}
                onChange={e=>handleFile(e.target.files[0])}/>
              {file ? (
                <>
                  <div style={{
                    width:64,height:64,borderRadius:16,margin:"0 auto 16px",
                    background:"rgba(124,252,0,0.08)",border:"1px solid rgba(124,252,0,0.22)",
                    display:"flex",alignItems:"center",justifyContent:"center"
                  }}>
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#7CFC00" strokeWidth="1.5">
                      <path d="M9 12l2 2 4-4M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2z"/>
                    </svg>
                  </div>
                  <p style={{fontSize:16,fontWeight:600,color:"#7CFC00",marginBottom:5}}>{file.name}</p>
                  <p style={{fontSize:13,color:"rgba(124,252,0,0.45)"}}>{(file.size/1024).toFixed(1)} KB · Click to change</p>
                </>
              ) : (
                <>
                  <div style={{
                    width:64,height:64,borderRadius:16,margin:"0 auto 16px",
                    background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",
                    display:"flex",alignItems:"center",justifyContent:"center"
                  }}>
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.22)" strokeWidth="1.5">
                      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                    </svg>
                  </div>
                  <p style={{fontSize:16,fontWeight:600,color:"rgba(255,255,255,0.72)",marginBottom:6}}>
                    Drop your resume here
                  </p>
                  <p style={{fontSize:13,color:"rgba(255,255,255,0.2)"}}>PDF only · Max 10 MB</p>
                </>
              )}
            </div>

            {error && (
              <div style={{
                marginTop:12,padding:"12px 16px",borderRadius:12,fontSize:13,lineHeight:1.6,
                background:"rgba(226,75,74,0.07)",border:"1px solid rgba(226,75,74,0.22)",color:"#ff7070",
                whiteSpace:"pre-line"
              }}>{error}</div>
            )}

            <button onClick={analyze} disabled={!file} style={{
              width:"100%",marginTop:14,padding:"16px 0",borderRadius:14,
              fontSize:15,fontWeight:600,cursor:file?"pointer":"not-allowed",border:"none",
              letterSpacing:"0.02em",transition:"all 0.2s ease",
              background:file?"linear-gradient(135deg,#00D4FF,#0050FF)":"rgba(255,255,255,0.04)",
              color:file?"#000":"rgba(255,255,255,0.18)",
              boxShadow:file?"0 0 32px rgba(0,212,255,0.2)":"none"
            }}>
              {file ? "Analyze Resume →" : "Select a PDF to continue"}
            </button>

            <div style={{display:"flex",gap:8,marginTop:16,flexWrap:"wrap"}}>
              {["Domain Detection","Top 5 Roles","Skill Scoring","10 Job Portals"].map((f,i)=>(
                <span key={i} style={{
                  padding:"5px 12px",borderRadius:99,fontSize:11,
                  background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.065)",
                  color:"rgba(255,255,255,0.32)"
                }}>{f}</span>
              ))}
            </div>
          </div>
        )}

        {/* ── ANALYZING SCREEN ── */}
        {step === "analyzing" && (
          <div style={{ animation:"fadeUp 0.4s ease both" }}>
            <div style={{
              padding:"52px 32px",borderRadius:20,textAlign:"center",
              background:"rgba(255,255,255,0.018)",border:"1px solid rgba(255,255,255,0.055)"
            }}>
              <div style={{
                width:52,height:52,margin:"0 auto 22px",
                border:"2px solid rgba(255,255,255,0.05)",
                borderTopColor:"#00D4FF",borderRadius:"50%",
                animation:"spin 0.7s linear infinite",
                boxShadow:"0 0 18px rgba(0,212,255,0.22)"
              }}/>
              <p style={{fontSize:18,fontWeight:600,color:"#fff",marginBottom:5}}>Analyzing your resume</p>
              <p style={{fontSize:13,color:"rgba(255,255,255,0.25)",marginBottom:34}}>{file?.name}</p>
              <div style={{textAlign:"left",display:"flex",flexDirection:"column",gap:8}}>
                {LOADING_STEPS.map((s,i)=>{
                  const done=i<loadStep, active=i===loadStep;
                  return (
                    <div key={i} style={{
                      display:"flex",alignItems:"center",gap:11,padding:"10px 14px",
                      borderRadius:10,transition:"all 0.28s ease",
                      background:active?"rgba(0,212,255,0.045)":"transparent",
                      border:`1px solid ${active?"rgba(0,212,255,0.16)":"transparent"}`
                    }}>
                      <div style={{
                        width:20,height:20,borderRadius:"50%",flexShrink:0,
                        display:"flex",alignItems:"center",justifyContent:"center",
                        background:done?"#00D4FF":active?"transparent":"rgba(255,255,255,0.04)",
                        border:`1px solid ${done?"#00D4FF":active?"#00D4FF":"rgba(255,255,255,0.07)"}`,
                        boxShadow:active?"0 0 9px rgba(0,212,255,0.4)":"none"
                      }}>
                        {done
                          ? <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="3"><path d="M5 12l5 5L20 7"/></svg>
                          : active
                          ? <div style={{width:6,height:6,borderRadius:"50%",background:"#00D4FF",animation:"pulse 0.8s ease infinite"}}/>
                          : null
                        }
                      </div>
                      <span style={{
                        fontSize:13,fontWeight:active?500:400,
                        color:done?"rgba(255,255,255,0.3)":active?"#fff":"rgba(255,255,255,0.18)"
                      }}>{s}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ── RESULTS SCREEN ── */}
        {step === "result" && result && meta && (
          <div>

            {/* Domain banner */}
            <div style={{
              padding:"22px 24px",borderRadius:20,marginBottom:12,
              background:meta.glow,border:`1px solid ${accent}25`,
              boxShadow:`0 0 48px ${meta.glow}`,
              animation:"fadeUp 0.5s ease both"
            }}>
              <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}>
                <span style={{width:7,height:7,borderRadius:"50%",background:accent,boxShadow:`0 0 8px ${accent}`,display:"inline-block"}}/>
                <span style={{fontSize:11,color:`${accent}75`,letterSpacing:"0.12em",textTransform:"uppercase"}}>Domain detected</span>
              </div>
              <h2 style={{fontSize:26,fontWeight:700,color:accent,marginBottom:4}}>{meta.label}</h2>
              <p style={{fontSize:13,color:"rgba(255,255,255,0.32)"}}>
                From&nbsp;<span style={{color:"rgba(255,255,255,0.5)"}}>{file?.name}</span>
                &nbsp;·&nbsp;{result.char_count?.toLocaleString()} chars extracted
              </p>
            </div>

            {/* Stats row */}
            <div style={{display:"flex",gap:10,marginBottom:12,animation:"fadeUp 0.5s ease 0.08s both"}}>
              {[
                { label:"Roles found",    val: top5.length },
                { label:"Top confidence", val: `${top5[0]?.confidence.toFixed(0)}%` },
                { label:"Skills matched", val: skills.length },
                { label:"Skill score",    val: `${result.skill_score ?? 0}%` },
              ].map((s,i)=>(
                <div key={i} style={{
                  flex:1,padding:"14px 16px",borderRadius:14,
                  background:"rgba(255,255,255,0.025)",border:"1px solid rgba(255,255,255,0.065)"
                }}>
                  <p style={{fontSize:10,color:"rgba(255,255,255,0.3)",letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:7}}>{s.label}</p>
                  <p style={{fontSize:20,fontWeight:700,color:accent,fontFamily:"monospace"}}>{s.val}</p>
                </div>
              ))}
            </div>

            {/* Top 5 Predicted Roles */}
            <div style={{
              padding:"22px 24px",borderRadius:20,marginBottom:12,
              background:"rgba(255,255,255,0.018)",border:"1px solid rgba(255,255,255,0.065)",
              animation:"fadeUp 0.5s ease 0.15s both"
            }}>
              <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:18}}>
                <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",textTransform:"uppercase",letterSpacing:"0.12em"}}>
                  Predicted job roles
                </p>
                <span style={{fontSize:11,color:`${accent}70`}}>{top5.length} matches</span>
              </div>

              <div style={{display:"flex",flexDirection:"column",gap:10}}>
                {visibleRoles.map((item,i)=>(
                  <div key={i} style={{
                    display:"flex",alignItems:"center",gap:14,padding:"14px 16px",
                    borderRadius:14,
                    background:i===0?`${accent}0A`:"rgba(255,255,255,0.015)",
                    border:`1px solid ${i===0?`${accent}25`:"rgba(255,255,255,0.045)"}`,
                    animation:`fadeUp 0.38s ease ${0.18+i*0.08}s both`
                  }}>
                    <ConfidenceRing
                      value={item.confidence}
                      color={i===0?accent:i===1?"rgba(255,255,255,0.35)":"rgba(255,255,255,0.18)"}
                      size={i===0?68:56}
                    />
                    <div style={{flex:1}}>
                      {i===0 && (
                        <span style={{
                          display:"inline-block",fontSize:9,fontWeight:700,
                          padding:"2px 8px",borderRadius:99,marginBottom:5,
                          background:`${accent}1F`,color:accent,letterSpacing:"0.1em"
                        }}>BEST MATCH</span>
                      )}
                      <p style={{
                        fontSize:i===0?16:13,fontWeight:i===0?600:400,
                        color:i===0?"#fff":i===1?"rgba(255,255,255,0.6)":"rgba(255,255,255,0.38)"
                      }}>{item.role}</p>
                    </div>
                    <span style={{fontSize:11,color:"rgba(255,255,255,0.15)",fontFamily:"monospace",flexShrink:0}}>
                      #{i+1}
                    </span>
                  </div>
                ))}
              </div>

              {top5.length > 3 && (
                <button onClick={()=>setShowAll(p=>!p)} style={{
                  width:"100%",marginTop:12,padding:"9px 0",borderRadius:10,fontSize:13,
                  cursor:"pointer",background:"rgba(255,255,255,0.03)",
                  color:"rgba(255,255,255,0.4)",border:"1px solid rgba(255,255,255,0.06)",
                  transition:"background 0.16s"
                }}
                  onMouseEnter={e=>e.currentTarget.style.background="rgba(255,255,255,0.06)"}
                  onMouseLeave={e=>e.currentTarget.style.background="rgba(255,255,255,0.03)"}
                >
                  {showAll ? "Show less ↑" : `Show all ${top5.length} predictions ↓`}
                </button>
              )}
            </div>

            {/* Skill score bar */}
            {result.skill_score > 0 && (
              <div style={{
                padding:"22px 24px",borderRadius:20,marginBottom:12,
                background:"rgba(255,255,255,0.018)",border:"1px solid rgba(255,255,255,0.065)",
                animation:"fadeUp 0.5s ease 0.28s both"
              }}>
                <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",textTransform:"uppercase",letterSpacing:"0.12em",marginBottom:16}}>
                  Domain skill match
                </p>
                <ScoreBar label={meta.label} value={result.skill_score} color={accent}/>
                {result.cross_skills && Object.entries(result.cross_skills).slice(0,2).map(([d,_],i)=>(
                  <ScoreBar
                    key={i}
                    label={DOMAIN_META[d]?.label || d}
                    value={(_.length / 10) * 100}
                    color={DOMAIN_META[d]?.color || "#555"}
                  />
                ))}
              </div>
            )}

            {/* Skills */}
            {skills.length > 0 && (
              <div style={{
                padding:"22px 24px",borderRadius:20,marginBottom:12,
                background:"rgba(255,255,255,0.018)",border:"1px solid rgba(255,255,255,0.065)",
                animation:"fadeUp 0.5s ease 0.35s both"
              }}>
                <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:14}}>
                  <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",textTransform:"uppercase",letterSpacing:"0.12em"}}>
                    Detected skills
                  </p>
                  <span style={{fontSize:11,color:`${accent}70`}}>{skills.length} found</span>
                </div>
                <div style={{display:"flex",flexWrap:"wrap",gap:7}}>
                  {skills.map((s,i)=>(
                    <SkillTag key={i} skill={s} color={accent} delay={0.36+i*0.03}/>
                  ))}
                </div>
              </div>
            )}

            {/* Job Links — all 10 */}
            <div style={{
              padding:"22px 24px",borderRadius:20,marginBottom:18,
              background:"rgba(255,255,255,0.018)",border:"1px solid rgba(255,255,255,0.065)",
              animation:"fadeUp 0.5s ease 0.44s both"
            }}>
              <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:14}}>
                <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",textTransform:"uppercase",letterSpacing:"0.12em"}}>
                  Live job searches
                </p>
                <span style={{fontSize:11,color:`${accent}70`}}>"{result.top_role}"</span>
              </div>
              <div style={{display:"flex",flexDirection:"column",gap:7}}>
                {links.map((link,i)=>(
                  <JobLinkRow key={i} name={link.name} url={link.url} index={i} accent={accent}/>
                ))}
              </div>
            </div>

            {/* Action buttons */}
            <div style={{display:"flex",gap:10,animation:"fadeUp 0.5s ease 0.52s both"}}>
              <button onClick={reset} style={{
                flex:1,padding:"14px 0",borderRadius:12,fontSize:14,fontWeight:500,
                cursor:"pointer",background:"rgba(255,255,255,0.04)",
                color:"rgba(255,255,255,0.52)",border:"1px solid rgba(255,255,255,0.07)",
                transition:"background 0.16s"
              }}
                onMouseEnter={e=>e.currentTarget.style.background="rgba(255,255,255,0.07)"}
                onMouseLeave={e=>e.currentTarget.style.background="rgba(255,255,255,0.04)"}
              >
                ← Analyze another
              </button>
              <button
                onClick={()=>links.forEach(l=>window.open(l.url,"_blank"))}
                style={{
                  flex:1,padding:"14px 0",borderRadius:12,fontSize:14,fontWeight:600,
                  cursor:"pointer",border:"none",
                  background:`linear-gradient(135deg,${accent},${accent}90)`,
                  color:"#000",boxShadow:`0 0 24px ${meta.glow}`
                }}
              >
                Open all 10 tabs →
              </button>
            </div>
          </div>
        )}

        <p style={{textAlign:"center",fontSize:10,color:"rgba(255,255,255,0.1)",marginTop:52,letterSpacing:"0.08em"}}>
          TF-IDF · LOGISTIC REGRESSION · NLP DOMAIN CLASSIFIER · 15 DOMAINS
        </p>
      </div>
    </div>
  );
}