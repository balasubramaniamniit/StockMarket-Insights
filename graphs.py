

# PLOTLY GRAPHS
import plotly.graph_objects as go
import plotly.express as px


def bar_chart(df):
    fig = go.Figure([go.Bar(x=list(df.Month_name), y=df.fbcounts)])
    fig.update_traces(
        marker=dict(color='#0000A0')
    )
    fig.update_layout(
        bargap=0.85,
        yaxis=dict(title='Feedback Volume'),
        font=dict(size=14),
        title=dict(text="<b>Volume of Feedback Each Month</b>"),
    )
    return fig

def update_sentiment_linechart(df,x,y,color):
    stock_sentiment_line_fig = px.line(df, x=x, y=y, color=color)
    stock_sentiment_line_fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=45, label="45m", step="minute", stepmode="backward"),
                dict(count=1, label="HTD", step="hour", stepmode="todate"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    stock_sentiment_line_fig.update_layout(
        title='Users Sentiment from Social Media for Selected Ticker ',
        yaxis_title='Sentiment Score',
        xaxis_title='Date'
    )
    stock_sentiment_line_fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False,plot_bgcolor='#5B5959')

    return stock_sentiment_line_fig

def candlestick_chart(data):
    #declare figure
    fig = go.Figure()

    #Candlestick
    fig.add_trace(go.Candlestick(x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'], name = 'market data'))

    # Add titles
    fig.update_layout(
        title='Stock Price for Selected Ticker',
        yaxis_title='Stock Price ')
    fig.update_xaxes(
        rangebreaks=[

            dict(bounds=[17, 9], pattern="hour"),
           dict(bounds=[6, 1], pattern="day of week"),  # hide hours outside of 9am-5pm
        ]),

    # X-Axes
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=45, label="45m", step="minute", stepmode="backward"),
                dict(count=1, label="HTD", step="hour", stepmode="todate"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, plot_bgcolor='#5B5959')

    #Show
    return fig

def update_stock_sentiment_funnel(df,x,y,text,color):
     stock_sentiment_funnel_fig = px.funnel(df, x=x, y=y, text=text, color=color)
     stock_sentiment_funnel_fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(count=12, label="12h", step="hour", stepmode="backward"),
                    dict(count=24, label="24h", step="hour", stepmode="backward"),
                    dict(count=48, label="48h", step="hour", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
     stock_sentiment_funnel_fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False,plot_bgcolor='#5B5959')
     
     return stock_sentiment_funnel_fig
