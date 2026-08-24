with open("frontend/src/lib/api.ts", "r") as f:
    text = f.read()

text = text.replace("export async function getDashboardReport(): Promise<string> {\n  try {\n    const response = await fetch(`${API_BASE}/api/dashboard/report`);", "export async function getDashboardReport(language: string = 'en'): Promise<string> {\n  try {\n    const response = await fetch(`${API_BASE}/api/dashboard/report?language=${language}`);")

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(text)

with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    dash = f.read()

dash = dash.replace("const rep = await getDashboardReport();", "const rep = await getDashboardReport(language);")
dash = dash.replace("loadReport();", "// loadReport() called in useEffect below")
dash = dash.replace("getExchangeSignals()", "getExchangeSignals()\n      ]);\n      setStats(s);\n      setOutbreaks(o);\n      setStates(c);\n      setHealthData(h);\n      setSignals(sig.signals || []);\n    }\n    loadData();\n  }, []);\n\n  useEffect(() => {\n    loadReport();\n  }, [language]);\n\n  const loadReport = async () => {\n    setLoadingReport(true);\n    const rep = await getDashboardReport(language);\n    setReport(rep || \"No report data available at this time.\");\n    setLoadingReport(false);\n  };\n\n  // DUMMY COMMENT TO REPLACE")

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(dash)
