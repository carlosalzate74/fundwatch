let filters = {}

// Get selected values from years
$("#years").on("change", function() {
	filters["years"] = $("#years").select2("val");
	sendFilters(filters)
})

// Get selected values from months
$("#months").on("change", function() {
	filters["months"] = $("#months").select2("val");
	sendFilters(filters)
})

// Get selected values from category
$("#categories").on("change", function(event) {
	filters["categories"] = $("#categories").select2("val");
	sendFilters(filters)
})

const sendFilters = function(filters){
	d3.json("/filters", {
		method: "POST",
		body: JSON.stringify({
			filters: filters
		}),
		headers: {
	        "Content-type": "application/json; charset=UTF-8"
	    }
	}).then(function(data) {
		d3.select("#transactions").text(data.transactions)
		d3.select("#credit_amt .myvalue").text(data.credit_amt)
		d3.select("#cash_amt .myvalue").text(data.cash_amt)
		d3.select("#expenses .myvalue").text(data.expenses)
		d3.select("#income .myvalue").text(data.income)
		d3.select("#savings_rate .myvalue").text(data.savings_rate)

		subCatPlot(data)
		mainPlot(data.exp_key, data.exp_val)
		
	});
}

sendFilters(filters)