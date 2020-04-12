const getMainPlot = function(){
	d3.json("/mainplot").then(function(data){
		mainPlot(data.mainplot_key, data.mainplot_val)
	})
}

const mainPlot = function(key, value){
	let expenses = {
		x: key,
		y: value,
		type: "bar",
		name: "Expenses",
		marker:{
			color: "#2C3531"
		}
	}

	let layout = {
		title: "Expenses by Category",
		height: 400,
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
	if ($("#mainplot").length > 0)
		Plotly.react("mainplot", data, layout)
}
