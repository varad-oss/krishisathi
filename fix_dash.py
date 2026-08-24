import re

with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    dash = f.read()

# Add language to loadReport
dash = dash.replace("const loadReport = async () => {\n    setLoadingReport(true);\n    const rep = await getDashboardReport();", "const loadReport = async () => {\n    setLoadingReport(true);\n    const rep = await getDashboardReport(language);")

# Re-run loadReport when language changes!
dash = dash.replace("loadData();\n  }, []);", "loadData();\n  }, []);\n\n  useEffect(() => {\n    if (stats) loadReport();\n  }, [language]);")

dash = dash.replace("{state.name}", "{t(state.name, language)}")
dash = dash.replace("{state.top_crop}", "{t(state.top_crop, language)}")
dash = dash.replace("{sig.severity}", "{t(sig.severity, language)}")
dash = dash.replace("{sig.message}", "{t(sig.message, language)}")

# Fix graph x-axis data (which hasn't been mapped with translations)
dash = dash.replace("data={filteredHealth}", "data={filteredHealth.map(h => ({...h, region: t(h.region, language)}))}")

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(dash)
