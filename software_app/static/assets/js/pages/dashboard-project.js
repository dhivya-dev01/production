'use strict';
$(document).ready(function() {
    // [ type-chart ] start
    // $(function() {
    //    // Themes begin
    //    am4core.useTheme(am4themes_animated);
    //    // Themes end
    //    // Create chart instance
    //    var chart = am4core.create("type-chart", am4charts.PieChart);
    //    // Add data
    //     chart.data = [{
    //                 "status": "Pending",
    //                 "count": {{ status_counts.pending }}
    //             },
    //             {
    //                 "status": "Completed",
    //                 "count": {{ status_counts.completed }}
    //             },
    //             {
    //                 "status": "Hold",
    //                 "count": {{ status_counts.hold }}
    //             },
    //             {
    //                 "status": "Partial",
    //                 "count": {{ status_counts.partial }}
    //             },
    //             {
    //                 "status": "Cancelled",
    //                 "count": {{ status_counts.cancelled }}
    //             },
    //             {
    //                 "status": "Opened",
    //                 "count": {{ status_counts.opened }}
    //             }
    //         ];
    //    // Add label
    //    chart.innerRadius = 35;

    //    // Add and configure Series
    //    var pieSeries = chart.series.push(new am4charts.PieSeries());
    //    pieSeries.dataFields.value = "count";
    //    pieSeries.dataFields.category = "status";
    //    pieSeries.labels.template.disabled = true;
    //    pieSeries.ticks.template.disabled = true;
    //    pieSeries.colors.step = 3;
    // });
    // [ type-chart ] end

    // [ rating ] start
    $('#example-1to10').barrating('show', {
       theme: 'bars-1to10',
       readonly: true,
       showSelectedRating: false
    });
    // [ rating ] end

    // [ new-scroll ] start
    var px = new PerfectScrollbar('.new-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    // [ new-scroll ] end

    // [ user-scroll ] start
    var px = new PerfectScrollbar('.user-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    // [ user-scroll ] end
    
});
