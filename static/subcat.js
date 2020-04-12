const getTopTenSubCat = function(){
	d3.json("/toptensubcat").then(function(data){
		subCatPlot(data)
	})
}

const subCatPlot = function(data){
	let expenses = {
		x: data.subcat_key,
		y: data.subcat_val,
		type: "bar",
		name: "Expenses",
		marker:{
			color: "#2C3531"
		}
	}

	let layout = {
		title: "Expenses by Subcategory",
		height: 630,
		font: {
			size: 14
		},
		xaxis: {
			color: "#2C3531"
		},
        yaxis: {
			title: "Dollars"
			
        }
	}
	data = [expenses]
	if ($("#subcategories").length > 0)
		Plotly.react("subcategories", data, layout)
}
