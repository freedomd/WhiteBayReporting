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
	var mode = $("#mode").val();
	if(tab == $("#tab").val()) {
		new_order = (parseInt($("#order").val())+1)%2;
	} else {
		new_order = 0;
	}

	$("#tab").val(tab);
	$("#order").val(new_order);
	if(mode == "g") {
		getReportList(1);
	} else if(mode == "q") {
		queryReportList(1);
	}
}

function getReportList(strpage) {
	$("html,body").animate({scrollTop:0},0); // back to top
    Dajaxice.reports.getReportList(createReportList, {'tab': $("#tab").val(),
    											 'strorder': $("#order").val(),
    											 'account': $("#account").val(),
    											 'year': $("#year").val(), 
    							   				 'month': $("#month").val(),
    							   				 'day': $("#day").val(), 
    							   				 'strpage': strpage},
    						            		 {'error_callback': custom_error}); 		       
}

function queryReportList(strpage) {
	$("html,body").animate({scrollTop:0},0); // back to top
    Dajaxice.reports.queryReportList(createReportList, {'tab': $("#tab").val(),
    											 		'strorder': $("#order").val(),
    											 		'account': $("#account").val(),
    											 		'symbol': $("#symbol").val(),
    											 		'datefrom': $("#datefrom").val(), 
    							   				 		'dateto': $("#dateto").val(),
    							   				 		'strpage': strpage},
    						            		 		{'error_callback': custom_error}); 		       
}

function getSummaryReport() {
	html = "<div align='center'><img height='300' width='300' src='/assets/img/loading.gif'/></div>";
	$("#reports_container").empty();
	$("#message_container").empty(); 
	$("#message_container").append(html);
    Dajaxice.reports.getSummaryReport(getSummaryResponse, { 'account': $("#account").val(),
    														'symbol': $("#symbol").val(),
    											 			'datefrom': $("#datefrom").val(), 
    							   				 			'dateto': $("#dateto").val(),
    							   				 			'user_email': $("#user_email").val()},
    						            		 			{'error_callback': custom_error}); 		       
}

function getSummaryResponse(data) {
	$("#reports_container").empty(); // delete all the data
	$("#message_container").empty(); 
	var html = "";
	html += data.message;
	$("#message_container").append(html);
}


function createReportList(data) {
	var mode = $("#mode").val(); // query mode, g for get, q for query
	var number = data.report_list.length;
	$("#reports_container").empty(); // delete all the data
	$("#message_container").empty(); // delete all the data
	if(number == 0) {
		$("#reports_container").removeClass("data_container");
		var html = "";
		html += "No reports found.";
		$("#reports_container").append(html);
	} else {
		var html = "";
		
		html += "<table class='table table-striped table-bordered data_table'>";
		html += "<tr id='title'>";
		html += "<th><button class='btn btn-link tab' id='symbol' value=0 onclick=changeOrder(this.id)>Symbol</button></th>";
		html += "<th><button class='btn btn-link tab' id='SOD' value=0 onclick=changeOrder(this.id)>SOD</button></th>";
		html += "<th><button class='btn btn-link tab' id='mark' value=0 onclick=changeOrder(this.id)>Mark</button></th>";
		html += "<th><button class='btn btn-link tab' id='buys' value=0 onclick=changeOrder(this.id)>Buys</button></th>";
		html += "<th><button class='btn btn-link tab' id='buyAve' value=0 onclick=changeOrder(this.id)>Buy Ave</button></th>";
		html += "<th><button class='btn btn-link tab' id='sells' value=0 onclick=changeOrder(this.id)>Sells</button></th>";
		html += "<th><button class='btn btn-link tab' id='sellAve' value=0 onclick=changeOrder(this.id)>Sell Ave</button></th>";
		html += "<th><button class='btn btn-link tab' id='realizedPNL' value=0 onclick=changeOrder(this.id)>Realized PNL</button></th>";
		html += "<th><button class='btn btn-link tab' id='unrealizedPNL' value=0 onclick=changeOrder(this.id)>Unrealized PNL</button></th>";
		html += "<th><button class='btn btn-link tab' id='brokerCommission' value=0 onclick=changeOrder(this.id)>BrokerComm</button></th>";
		html += "<th><button class='btn btn-link tab' id='futureCommission' value=0 onclick=changeOrder(this.id)>FutureComm</button></th>";
		html += "<th><button class='btn btn-link tab' id='clearanceFees' value=0 onclick=changeOrder(this.id)>Clearance</button></th>";
		html += "<th><button class='btn btn-link tab' id='exchangeFees' value=0 onclick=changeOrder(this.id)>Exchange Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='nfaFees' value=0 onclick=changeOrder(this.id)>NFA Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='commission' value=0 onclick=changeOrder(this.id)>Commission</button></th>";
		html += "<th><button class='btn btn-link tab' id='secFees' value=0 onclick=changeOrder(this.id)>SEC Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='accruedSecFees' value=0 onclick=changeOrder(this.id)>Accrued SEC Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='ecnFees' value=0 onclick=changeOrder(this.id)>ECN Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='netPNL' value=0 onclick=changeOrder(this.id)>Net PNL</button></th>";
		html += "<th><button class='btn btn-link tab' id='LMV' value=0 onclick=changeOrder(this.id)>LMV</button></th>";
		html += "<th><button class='btn btn-link tab' id='SMV' value=0 onclick=changeOrder(this.id)>SMV</button></th>";
		html += "<th><button class='btn btn-link tab' id='EOD' value=0 onclick=changeOrder(this.id)>EOD</button></th>";
		html += "<th><button class='btn btn-link tab' id='closing' value=0 onclick=changeOrder(this.id)>Closing</button></th>";
		html += "<th><button class='btn btn-link tab' id='reportDate' value=0 onclick=changeOrder(this.id)>Report Date</button></th>";
		html += "</tr>";
		
		for(i = 0; i < number; i++) { // create a new list of reports
			var report = data.report_list[i].fields;
			var year = report.reportDate.substr(0, 4);
			var month = report.reportDate.substr(5, 2);
			var day = report.reportDate.substr(8, 2);
			var account = report.account;
			html += "<tr>";
			html += "<td><a href='/symbol/" + report.account + "/" + report.symbol + "/" + year + "/" + month + "/" + day + "/' >" + report.symbol + "</a></td>";
			html += "<td>" + addCommas(report.SOD) + "</td>";
			html += "<td>" + addCommas(report.mark.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.buys) + "</td>";
			html += "<td>" + addCommas(report.buyAve.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.sells) + "</td>";
			html += "<td>" + addCommas(report.sellAve.toFixed(2)) + "</td>";
			
			if(report.realizedPNL >=0) {
				html += "<td><span class='positive_data'>" + addCommas(report.realizedPNL.toFixed(2)) + "</span></td>";
			} else {
				html += "<td><span class='negative_data'>" + addCommas(report.realizedPNL.toFixed(2)) + "</span></td>";
			}
			
			if(report.unrealizedPNL >=0) {
				html += "<td><span class='positive_data'>" + addCommas(report.unrealizedPNL.toFixed(2)) + "</span></td>";
			} else {
				html += "<td><span class='negative_data'>" + addCommas(report.unrealizedPNL.toFixed(2)) + "</span></td>";
			}
			
			html += "<td>" + addCommas(report.brokerCommission.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.futureCommission.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.clearanceFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.exchangeFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.nfaFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.commission.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.secFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.accruedSecFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(report.ecnFees.toFixed(2)) + "</td>";

			if(report.netPNL >=0) {
				html += "<td><span class='positive_data'>" + addCommas(report.netPNL.toFixed(2)) + "</span></td>";
			} else {
				html += "<td><span class='negative_data'>" + addCommas(report.netPNL.toFixed(2)) + "</span></td>";
			}

			html += "<td>" + addCommas(report.LMV.toFixed(0)) + "</td>";
			html += "<td>" + addCommas(report.SMV.toFixed(0)) + "</td>";
			html += "<td>" + addCommas(report.EOD) + "</td>";
			html += "<td>" + addCommas(report.closing.toFixed(2)) + "</td>";
			html += "<td>" + report.reportDate + "</td>";
			html += "</tr>"
		}
		
		html += "</table>";
		
		html += "<div class='paginator'>";
		if(data.pp > 0) {
			if(mode == "g") {
				html += "<button class='btn btn-link' onclick='getReportList(" + data.pp + ");'>Previous</button>";
			} else if(mode == "q") {
				html += "<button class='btn btn-link' onclick='queryReportList(" + data.pp + ");'>Previous</button>";
			}
		}
		
		if(data.pp > 0 && data.np > 0) {
			html += "|";
		}
		
		if(data.np > 0) {
			if(mode == "g") {
				html += "<button class='btn btn-link' onclick='getReportList(" + data.np + ");'>Next</button>";
			} else if (mode == "q") {
				html += "<button class='btn btn-link' onclick='queryReportList(" + data.np + ");'>Next</button>";
			}
		}
		html += "</div><div style='clear:both;'></div>";
		
		$("#reports_container").addClass("data_container");
		$("#reports_container").append(html);
    }
}


function changeAccountOrder(tab) {
	var group = $("#groups").val();
	if(tab == $("#tab").val()) {
		new_order = (parseInt($("#order").val())+1)%2;
	} else {
		new_order = 0;
	}

	$("#tab").val(tab);
	$("#order").val(new_order);
	
	getAccountList(group);
}


function getAccountList(group_name) {
	$("#reports_container").empty();
	$("#message_container").empty(); 
    Dajaxice.reports.getAccountList(createAccountList, { 'group': group_name,
    												     'tab': $("#tab").val(),
    											 	     'strorder': $("#order").val() },
    						            		 	     {'error_callback': custom_error}); 		       
}


function createAccountList(data) {
	var number = data.account_list.length;
	$("#reports_container").empty(); // delete all the data
	$("#message_container").empty(); // delete all the data
	if(number == 0) {
		$("#reports_container").removeClass("account_container");
		var html = "";
		html += "No accounts found.";
		$("#reports_container").append(html);
	} else {
		var html = "";
		
		html += "<table class='table table-striped table-bordered data_table'>";
		html += "<tr id='title'>";
		html += "<th><button class='btn btn-link tab' id='account' value=0 onclick=changeAccountOrder(this.id)>Account</button></th>";
		html += "<th><button class='btn btn-link tab' id='realizedPNL' value=0 onclick=changeAccountOrder(this.id)>Realized PNL</button></th>";
		html += "<th><button class='btn btn-link tab' id='unrealizedPNL' value=0 onclick=changeAccountOrder(this.id)>Unrealized PNL</button></th>";
		html += "<th><button class='btn btn-link tab' id='commission' value=0 onclick=changeAccountOrder(this.id)>Commission</button></th>";
		html += "<th><button class='btn btn-link tab' id='secFees' value=0 onclick=changeAccountOrder(this.id)>SEC Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='accruedSecFees' value=0 onclick=changeAccountOrder(this.id)>Accrued SEC Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='ecnFees' value=0 onclick=changeAccountOrder(this.id)>ECN Fees</button></th>";
		html += "<th><button class='btn btn-link tab' id='netPNL' value=0 onclick=changeAccountOrder(this.id)>Net PNL</button></th>";
		html += "</tr>";
		
		for(i = 0; i < number; i++) { // create a new list of account summaries
			var account = data.account_list[i].fields;
			html += "<tr>";
			html += "<td><a href='/report/" + account.account + "/' >" + account.account + "</a></td>";
			
			if(account.realizedPNL >=0) {
				html += "<td><span class='positive_data'>" + addCommas(account.realizedPNL.toFixed(2)) + "</span></td>";
			} else {
				html += "<td><span class='negative_data'>" + addCommas(account.realizedPNL.toFixed(2)) + "</span></td>";
			}
			
			if(account.unrealizedPNL >=0) {
				html += "<td><span class='positive_data'>" + addCommas(account.unrealizedPNL.toFixed(2)) + "</span></td>";
			} else {
				html += "<td><span class='negative_data'>" + addCommas(account.unrealizedPNL.toFixed(2)) + "</span></td>";
			}

			html += "<td>" + addCommas(account.commission.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(account.secFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(account.accruedSecFees.toFixed(2)) + "</td>";
			html += "<td>" + addCommas(account.ecnFees.toFixed(2)) + "</td>";

			if(account.netPNL >=0) {
				html += "<td><span class='positive_data'>" + addCommas(account.netPNL.toFixed(2)) + "</span></td>";
			} else {
				html += "<td><span class='negative_data'>" + addCommas(account.netPNL.toFixed(2)) + "</span></td>";
			}
			
			html += "</tr>"
		}
		
		
		// total
		html += "<tr>";
		html += "<td><strong>Total</strong></td>";
			
		if(data.total_realizedPNL >=0) {
			html += "<td><span class='positive_data'>" + addCommas(data.total_realizedPNL.toFixed(2)) + "</span></td>";
		} else {
			html += "<td><span class='negative_data'>" + addCommas(data.total_realizedPNL.toFixed(2)) + "</span></td>";
		}
			
		if(data.total_unrealizedPNL >=0) {
			html += "<td><span class='positive_data'>" + addCommas(data.total_unrealizedPNL.toFixed(2)) + "</span></td>";
		} else {
			html += "<td><span class='negative_data'>" + addCommas(data.total_unrealizedPNL.toFixed(2)) + "</span></td>";
		}

		html += "<td>" + addCommas(data.total_commission.toFixed(2)) + "</td>";
		html += "<td>" + addCommas(data.total_secFees.toFixed(2)) + "</td>";
		html += "<td>" + addCommas(data.total_accruedSecFees.toFixed(2)) + "</td>";
		html += "<td>" + addCommas(data.total_ecnFees.toFixed(2)) + "</td>";

		if(data.total_netPNL >=0) {
			html += "<td><span class='positive_data'>" + addCommas(data.total_netPNL.toFixed(2)) + "</span></td>";
		} else {
			html += "<td><span class='negative_data'>" + addCommas(data.total_netPNL.toFixed(2)) + "</span></td>";
		}
			
		html += "</tr>";
		
		
		html += "</table>";
	
		$("#reports_container").addClass("account_container");
		$("#reports_container").append(html);
    }
}