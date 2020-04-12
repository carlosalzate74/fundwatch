d3.select("#incomebtn").on("click", function(event) {
	incomeamt = d3.select("#incomeamt").text(d3.select("#incomeamt").node().value).text()
	saveIncome(incomeamt)
})

const saveIncome = function (incomeamt){
	d3.json("/submitincome", {
		method: "POST",
		body: JSON.stringify({
			incomeamt: incomeamt
		}),
		headers: {
	        "Content-type": "application/json; charset=UTF-8"
	      }
	 })
	.then(function(data) {
		d3.select("#message").text(data.message) 
	 });
}

const getAnnualData = function(){
	d3.json("/ieplot/annual").then(function(data){
		iePlot(data, "%Y", 2)
	})
}

const getMonthlyData = function(){
	d3.json("/ieplot/monthly").then(function(data){
		iePlot(data, "%b-%y", 0)
	})
}

const iePlot = function(data, tickFormat, nTicks){
	let income = {
		x: data.inc_key,
		y: data.inc_val,
		type: "bar",
		name: "Income",
		connectgaps: true,
		marker:{
			color: "#3D9970"
		}
	}

	let expenses = {
		x: data.exp_key,
		y: data.exp_val,
		type: "bar",
		name: "Expenses",
		marker:{
			color: "#2C3531"
		}
	}

	let layout = {
		title: "Avg Income v. Expenses",
        barmode: "group",
        xaxis: {
            type: "date",
            tickformat: tickFormat,
            tickmode: "auto",
            nticks: nTicks
        },
        yaxis: {
            title: "Dollars"
        }
	}

	data = [income, expenses]
	if ($("#ieplot").length > 0)
		Plotly.react("ieplot", data, layout)
}

$("#monthly").on("change", function(event) {
	d3.select("#message").text("") 
	getMonthlyData()
})

$("#annual").on("change", function(event) {
	d3.select("#message").text("")
	getAnnualData()
})

$(window).on('load', function() {
    getAnnualData()
    getMainPlot()
	getTopTenSubCat()
})
