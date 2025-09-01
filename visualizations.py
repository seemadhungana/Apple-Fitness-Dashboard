import plotly.graph_objects as go
import calendar

def build_calendar_heatmap(year, month, cal_map):
    """
    Build a calendar heatmap showing daily calorie burn.
    
    Args:
        year: Year for the calendar (int)
        month: Month for the calendar (int, 1-12)
        cal_map: Dictionary mapping date objects to calorie values
        
    Returns:
        Plotly figure object with calendar heatmap
    """
    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    month_days = cal.monthdatescalendar(year, month)

    z = []  
    annotations = []

    # Build matrices for heatmap
    for row_idx, week in enumerate(month_days):
        row_vals = []
        for col_idx, d in enumerate(week):
            if d.month != month:
                row_vals.append(None)  # Use None for out-of-month dates
            else:
                cals_val = int(cal_map.get(d, 0))
                row_vals.append(cals_val if cals_val > 0 else 0)  # Use 0 for no workout days
                
                # Add day number annotation (top-left corner)
                annotations.append(
                    dict(
                        x=col_idx,
                        y=row_idx,
                        text=str(d.day),
                        showarrow=False,
                        font=dict(size=11, color="black", family="Arial"),
                        xanchor="left",
                        yanchor="top",
                        xshift=-35,  # Move further left
                        yshift=20    # Move up
                    )
                )
                
                # Add calories annotation (center) - only if there are calories
                if cals_val > 0:
                    annotations.append(
                        dict(
                            x=col_idx,
                            y=row_idx,
                            text=str(cals_val),
                            showarrow=False,
                            font=dict(size=16, color="white", family="Arial Black"),
                            xanchor="center",
                            yanchor="middle"
                        )
                    )
        z.append(row_vals)

    # Heatmap with better color scheme and grid
    heatmap = go.Heatmap(
        z=z,
        x=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
        y=[f"Week {i+1}" for i in range(len(month_days))],
        colorscale=[
            [0, '#f7f7f7'],      # Light gray for 0 calories
            [0.2, '#fee5d9'],    # Very light orange
            [0.4, '#fcbba1'],    # Light orange  
            [0.6, '#fc9272'],    # Medium orange
            [0.8, '#de2d26'],    # Red-orange
            [1.0, '#a50f15']     # Dark red
        ],
        showscale=True,
        hoverinfo="skip",
        zmin=0,
        zmid=150,  # Adjust based on your typical calorie range
        colorbar=dict(
            title="Calories Burned",
            titleside="right",
            tickmode="linear",
            tick0=0,
            dtick=50
        )
    )

    # Build figure
    fig = go.Figure(data=[heatmap])
    
    # Add grid lines
    for i in range(8):  # Vertical lines
        fig.add_shape(
            type="line",
            x0=i-0.5, y0=-0.5,
            x1=i-0.5, y1=len(month_days)-0.5,
            line=dict(color="white", width=2)
        )
    
    for i in range(len(month_days)+1):  # Horizontal lines
        fig.add_shape(
            type="line",
            x0=-0.5, y0=i-0.5,
            x1=6.5, y1=i-0.5,
            line=dict(color="white", width=2)
        )

    fig.update_layout(
        title=dict(
            text=f"Workout Calendar — {calendar.month_name[month]} {year}",
            font=dict(size=20, family="Arial", color="black"),
            x=0.5,  # Center the title
            xanchor="center"
        ),
        annotations=annotations,
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(7)),
            ticktext=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
            side="top",
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks=""
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(month_days))),
            ticktext=[f"Week {i+1}" for i in range(len(month_days))],
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks=""
        ),
        height=500,
        margin=dict(l=60, r=60, t=80, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig