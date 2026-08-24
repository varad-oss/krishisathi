import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    chat = f.read()

chat = chat.replace("import { t } from '@/lib/translations';", "import { t } from '@/lib/translations';\nimport { formatNumber } from '@/lib/utils';")

chat = chat.replace("${weatherData.temp}°C", "${formatNumber(weatherData.temp, language)}°C")
chat = chat.replace("{weatherData.humidity}%", "{formatNumber(weatherData.humidity, language)}%")
chat = chat.replace("{weatherData.wind} {t", "{formatNumber(weatherData.wind, language)} {t")
chat = chat.replace("{(weatherData.soil_moisture * 100).toFixed(1)}%", "{formatNumber(Number((weatherData.soil_moisture * 100).toFixed(1)), language)}%")
chat = chat.replace("{ndviData?.ndvi_score || '...'}", "{ndviData ? formatNumber(ndviData.ndvi_score, language) : '...'}")
chat = chat.replace("{alert.distance_km}", "{formatNumber(alert.distance_km, language)}")

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(chat)

