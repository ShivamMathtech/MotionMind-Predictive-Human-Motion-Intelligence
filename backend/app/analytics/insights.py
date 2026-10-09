def insights(current, previous=None):
    out=[]
    if current.get('total_reps',0): out.append(f"You completed {current['total_reps']} repetitions in this session.")
    if current.get('average_form') is not None:
        out.append(f"Your average heuristic form score was {current['average_form']}/100.")
    if previous:
        for key,label,unit in [('total_reps','Repetitions',''),('average_form','Form score',' points'),('average_rom','Average ROM','°')]:
            a=current.get(key); b=previous.get(key)
            if a is not None and b is not None:
                diff=round(a-b,1)
                out.append(f"{label} {'increased' if diff>=0 else 'decreased'} by {abs(diff)}{unit} versus your previous completed session with the same exercise sequence.")
    if not out: out=['Complete a tracked set to generate insights.']
    return out
