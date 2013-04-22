function custom_error(){
    // do nothing
}

function addCommas(number) {
	number += '';
	var x = number.split('.');
	var x1 = x[0];
	var x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}

function changeOrder(tab) {
	var mode = $("#mode").val(); // query mode, g for get, q for query
	
	if(tab == $("#tab").val()) {
		new_order = (parseInt($("#order").val())+1)%2;
	} else {
		new_order = 0;
	}

	$("#tab").val(tab);
	$("#order").val(new_order);
	
	if(mode == "g") {
		getTradeList(1);
	} else if(mode == "q") {
		queryTradeList(1);
	}
}


function queryTradeList(strpage) {
	$("html,body").animate({scrollTop:0},0); // back to top
	
	if($("#account").val() == "" && $("#symbol").val() == "" && $("#datefrom").val() == "" && $("#dateto").val() == "") {
		$("#trades_container").empty(); // delete all the data
		$("#trades_container").removeClass("data_container");
		var html = "";
		html += "No trades found.";
		$("#trades_container").append(html)
		return ;
	}
    Dajaxice.trades.queryTradeList(createTradeList, {'tab': $("#tab").val(),
    											 'strorder': $("#order").val(),
    											 'account': $("#account").val(),
    											 'symbol': $("#symbol").val(),
    											 'datefrom': $("#datefrom").val(), 
    							   				 'dateto': $("#dateto").val(),
    							   				 'strpage': strpage},
    						            		 {'error_callback': custom_error}); 		       
}


function getTradeList(strpage) {
	$("html,body").animate({scrollTop:0},0); // back to top
    Dajaxice.trades.getTradeList(createTradeList, {'tab': $("#tab").val(),
    											 'strorder': $("#order").val(),
    											 'account': $("#account").val(),
    											 'symbol': $("#symbol").val(),
    											 'year': $("#year").val(), 
    							   				 'month': $("#month").val(),
    							   				 'day': $("#day").val(),
    							   				 'strpage': strpage},
    						            		 {'error_callback': custom_error}); 		       
}

function createTradeList(data) {
	var mode = $("#mode").val(); // query mode, g for get, q for query
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
		html += "<tr id='title'>";
		html += "<th><button class='btn btn-link tab' id='account' value=0 onclick=changeOrder(this.id)>Account</button></th>";
		html += "<th><button class='btn btn-link tab' id='symbol' value=0 onclick=changeOrder(this.id)>Symbol</button></th>";
		html += "<th><button class='btn btn-link tab' id='securityType' value=0 onclick=changeOrder(this.id)>Security Type</button></th>";
		html += "<th><button class='btn btn-link tab' id='side' value=0 onclick=changeOrder(this.id)>Side</button></th>";
		html += "<th><button class='btn btn-link tab' id='quantity' value=0 onclick=changeOrder(this.id)>Quantity</button></th>";
		html += "<th><button class='btn btn-link tab' id='price' value=0 onclick=changeOrder(this.id)>Price</button></th>";
		html += "<th><button class='btn btn-link tab' id='route' value=0 onclick=changeOrder(this.id)>Route</button></th>";
		html += "<th><button class='btn btn-link tab' id='destination' value=0 onclick=changeOrder(this.id)>Destination</button></th>";
		html += "<th><button class='btn btn-link tab' id='liqFlag' value=0 onclick=changeOrder(this.id)>Liq Flag</button></th>";
		html += "<th><button class='btn btn-link tab' id='tradeDate' value=0 onclick=changeOrder(this.id)>Trade Date</button></th>";
		html += "<th><button class='btn btn-link tab' id='executionId' value=0 onclick=changeOrder(this.id)>Execution ID</button></th>";
		html += "</tr>";
				
		
		for(i = 0; i < number; i++) { // create a new list of trades
			var trade = data.trade_list[i].fields;
			html += "<tr>";
			html += "<td>" + trade.account + "</td>";
			html += "<td>" + trade.symbol + "</td>";
			html += "<td>" + trade.securityType + "</td>";
			if(trade.side == "SEL") {
				html += "<td>S</td>";
			} else if (trade.side == "BUY") {
				html += "<td>B</td>";
			} else {
				html += "<td>" + trade.side + "</td>";
			}
			html += "<td>" + addCommas(trade.quantity) + "</td>";
			html += "<td>" + addCommas(trade.price.toFixed(2)) + "</td>";
			html += "<td>" + trade.route + "</td>";
			html += "<td>" + trade.destination + "</td>";
			html += "<td>" + trade.liqFlag + "</td>";
			//html += "<td>" + addCommas(trade.commission.toFixed(2)) + "</td>";
			//html += "<td>" + addCommas(trade.clearanceFees.toFixed(2)) + "</td>";
			//html += "<td>" + addCommas(trade.secFees.toFixed(2)) + "</td>";
			html += "<td>" + trade.tradeDate.substring(0, 10) + "</td>";
			html += "<td>" + trade.executionId + "</td>";
			html += "</tr>"
		}
		
		html += "</table>"
		
		html += "<div class='paginator'>";
		if(data.pp > 0) {
			if(mode == "g") {
				html += "<button class='btn btn-link' onclick='getTradeList(" + data.pp + ");'>Previous</button>";
			} else if(mode == "q") {
				html += "<button class='btn btn-link' onclick='queryTradeList(" + data.pp + ");'>Previous</button>";
			}
		}
		
		if(data.pp > 0 && data.np > 0) {
			html += "|";
		}
		
		if(data.np > 0) {
			if(mode == "g") {
				html += "<button class='btn btn-link' onclick='getTradeList(" + data.np + ");'>Next</button>";
			} else if (mode == "q") {
				html += "<button class='btn btn-link' onclick='queryTradeList(" + data.np + ");'>Next</button>";
			}
		}
		html += "</div><div style='clear:both;'></div>";
		
		$("#trades_container").addClass("data_container");
		$("#trades_container").append(html);
    }
}
