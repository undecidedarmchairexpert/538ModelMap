import us
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go


county_ev = ["NE-1", "NE-2", "NE-3", "ME-1", "ME-2"]


forecast_national = pd.read_csv("https://projects.fivethirtyeight.com/2020-general-data/presidential_national_toplines_2020.csv", parse_dates=["modeldate"])
forecast_state = pd.read_csv("https://projects.fivethirtyeight.com/2020-general-data/presidential_state_toplines_2020.csv", parse_dates=["modeldate"])


# Grab information to make the top overall probability plot
forecast_national_latest = forecast_national.loc[forecast_national.modeldate == forecast_national.modeldate.max()]

probability_r = round(forecast_national_latest.iloc[0].ecwin_inc*100, 2)
probability_d = round(forecast_national_latest.iloc[0].ecwin_chal*100, 2)
probability_o = 100 - (probability_d + probability_r)

plt.style.use('fivethirtyeight')

fig, ax = plt.subplots(figsize=(7, 1), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(-0.8, 0.8)

ax.barh("Model", probability_d, label='Democratic', color="#00AEF3")
ax.text(1, "Model", str(probability_d)+"%", size=10, color="white", horizontalalignment='left', verticalalignment='center')

ax.barh("Model", probability_o, left=probability_d, label='Other', color="grey")

ax.barh("Model", probability_r, left=probability_o+probability_d, label='Republican', color="#E81B23")
ax.text(99, "Model", str(probability_r)+"%", size=10, color="white", horizontalalignment='right', verticalalignment='center')

ax.text(0, 0.95, 'Joe Biden\nDemocrat', size=10, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
ax.text(1, 0.95, 'Donald Trump\nRepublican', size=10, horizontalalignment='right', verticalalignment='center', transform=ax.transAxes)

ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
plt.box(False)

plt.savefig('model_probability.png', transparent=True, bbox_inches='tight')


# Grab the information to make the choropleth state-by-state map
forecast_state_latest = forecast_state.loc[forecast_state.modeldate == forecast_state.modeldate.max()]
forecast_state_latest_county_ev = forecast_state_latest.loc[forecast_state_latest.state.isin(county_ev)]
forecast_state_latest_state_ev = forecast_state_latest.loc[~forecast_state_latest.state.isin(county_ev)].reset_index(drop=True)

state_abbr = list()
for state in forecast_state_latest_state_ev.state:
    state_abbr.append(us.states.lookup(state).abbr)
forecast_state_latest_state_ev["state_abbr"] = state_abbr

for col in forecast_state_latest_state_ev.columns:
    forecast_state_latest_state_ev[col] = forecast_state_latest_state_ev[col].astype(str)

forecast_state_latest_state_ev['winstate_num_chal'] = forecast_state_latest_state_ev['winstate_chal'].apply(lambda x: float(x))
forecast_state_latest_state_ev['winstate_num_inc'] = forecast_state_latest_state_ev['winstate_inc'].apply(lambda x: float(x))

forecast_state_latest_state_ev["winperc_inc"] = round(forecast_state_latest_state_ev['winstate_num_inc'].multiply(100), 2).apply(lambda x: str(x) + "%")
forecast_state_latest_state_ev["winperc_chal"] = round(forecast_state_latest_state_ev['winstate_num_chal'].multiply(100), 2).apply(lambda x: str(x) + "%")

forecast_state_latest_state_ev['text'] = forecast_state_latest_state_ev['state'] + '<br>' + \
    'Donald Trump ' + forecast_state_latest_state_ev["winperc_inc"] + '<br>' + \
    'Joe Biden ' + forecast_state_latest_state_ev["winperc_chal"] + '<br>'

fig = go.Figure(data=go.Choropleth(
    locations=forecast_state_latest_state_ev['state_abbr'],
    z=forecast_state_latest_state_ev['winstate_inc'],
    locationmode='USA-states',
    colorscale=[[0, "rgb(0, 174, 243)"],
                [0.5, "rgb(245,245,245)"],
                [1, "rgb(232, 27, 35)"]],
    autocolorscale=False,
    text=forecast_state_latest_state_ev['text'], # hover text
    marker_line_color='grey',
    # showscale=False,
))

fig.update_layout(
    geo = dict(
        scope='usa',
        projection=go.layout.geo.Projection(type = 'albers usa'),
        showlakes=False,
    ),
)
fig.show()
fig.write_html("choropleth_map.html")
fig.write_image("choropleth_map.png")