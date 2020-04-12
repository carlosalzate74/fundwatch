d3.select("#category").on("change", function(event) {
    category = d3.select("#category")._groups[0][0].value
    $("#sub_category").find("option:not(:first)").remove();
    populate(category)
})

const populate = function (category){
    d3.json("/filtersubcat", {
        method: "POST",
        body: JSON.stringify({
            category: category
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
     })
    
    .then(function(data) {
        fill_subcat = d3.select("#sub_category").selectAll("options").data(data).enter()
        .append("option")
        fill_subcat.text(function(d) {return d}).attr("value", function(d) {return d})
        
     });
}