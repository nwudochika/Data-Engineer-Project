import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:Plan10boy%26@localhost:5432/MyDB")
df = pd.read_sql("SELECT * FROM curated_weather ORDER BY date", engine)

fig = px.line(df, x="date", y="mean_temp", color="source", title="Weather Trends (Public vs Fake)")
fig.show()

