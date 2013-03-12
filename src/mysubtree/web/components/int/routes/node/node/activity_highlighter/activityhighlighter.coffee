#= require common
#= require int/misc/menu/menu
#= require int/misc/utils/utils
utils = window.utils

activity_highlight_color = utils.getCSS(".activity-highlight-color").color

adjust = (selectedTime, times) ->
    utils.save(selectedTime, "activityHighlighter-time")
    
    highlight = true
    for time in times
        if time != "off"
            color = if highlight then activity_highlight_color else "auto"
            utils.setCSS(".timesince.#{time}", "color: #{color}")
            utils.setCSS(".type.#{time}", "color: #{color}")
        if time == selectedTime
            highlight = false # for next times

$(document).ready( ->
    activityHighlighter = createActivityHighlighter()
    $(".activity-highlighter-open").css("display", "inline-block").click( ->
        activityHighlighter.toggle()
        $(".activity-highlighter-area") #.toggleClass("collapsed")
    )
)

createActivityHighlighter = ->
    activityHighlighter = $(".activity-highlighter")
    if activityHighlighter.length
        $(".activity-highlighter").css("display", "inline").toggle()
        timeselect = activityHighlighter.children("select.time")[0]
        timeslider = activityHighlighter.children(".time-slider")

        times = utils.get_options(timeselect)
        timeselect.value = utils.load("activityHighlighter-time") or times[1]
        adjust(timeselect.value, times)
        
        timeslider.slider({
            min: 0,
            max: times.length - 1,
            range: "min",
            value: timeselect.selectedIndex,
            slide: (event, ui) ->
                timeselect.value = times[ui.value]
                adjust(timeselect.value, times)
        })
        
        $(timeselect).change( ->
            timeslider.slider("value", this.selectedIndex);
            adjust(timeselect.value, times)
        )
    return activityHighlighter