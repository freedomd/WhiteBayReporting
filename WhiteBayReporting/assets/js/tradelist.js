function custom_error(){
    // do nothing
}

function getTradeList(strpage) {
	$("html,body").animate({scrollTop:0},0); // back to top
	
	if($("#account").val() == "" && $("#symbol").val() == "" && $("#datefrom").val() == "" && $("#dateto").val() == "") {
		$("#trades_container").empty(); // delete all the data
		$("#trades_container").removeClass("data_container");
		var html = "";
		html += "No trades found.";
		$("#trades_container").append(html)
		return ;
	}
    Dajaxice.trades.tradeQuery(createTradeList, {'account': $("#account").val(),
    											 'symbol': $("#symbol").val(),
    											 'datefrom': $("#datefrom").val(), 
    							   				 'dateto': $("#dateto").val(),
    							   				 'strpage': strpage},
    						            		 {'error_callback': custom_error}); 		       
}


function createTradeList(data) {
	var number = data.trade_list.length;
	$("#trades_container").empty(); // delete all the data
	if(number == 0) {
		$("#trades_container").removeClass("data_container");
		var html = "";
		html += "No trades found.";
		$("#trades_container").append(html);
	} else {
		var html = "";
		html += "<table class='table table-striped table-bordered data_table'>";
		html += "<tr><th>Account</th><th>Symbol</th><th>Side</th><th>Quantity</th><th>Price</th><th>Date</th><th>Execution ID</th></tr>";
		
		
		for(i = 0; i < number; i++) { // create a new list of trades
			html += "<tr>";
			html += "<td>" + data.trade_list[i].fields.account + "</td>";
			html += "<td>" + data.trade_list[i].fields.symbol + "</td>";
			html += "<td>" + data.trade_list[i].fields.side + "</td>";
			html += "<td>" + data.trade_list[i].fields.quantity + "</td>";
			html += "<td>" + data.trade_list[i].fields.price.toFixed(2) + "</td>";
			html += "<td>" + data.trade_list[i].fields.tradeDate.substring(0, 10) + "</td>";
			html += "<td>" + data.trade_list[i].fields.executionId + "</td>";
			html += "</tr>"
		}
		
		html += "</table>"
		
		html += "<div class='paginator'>";
		if(data.pp > 0) {
			html += "<button class='btn btn-link' onclick='getTradeList(" + data.pp + ");'>Previous</button>";
		}
		
		if(data.pp > 0 && data.np > 0) {
			html += "|";
		}
		
		if(data.np > 0) {
			html += "<button class='btn btn-link' onclick='getTradeList(" + data.np + ");'>Next</button>";
		}
		html += "</div><div style='clear:both;'></div>";
		
		$("#trades_container").addClass("data_container");
		$("#trades_container").append(html);
    }
}
