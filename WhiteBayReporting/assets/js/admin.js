function custom_error(){
    // do nothing
}

function validate_email(field) {
	with (field) {
		if (value == null || value == "") {
			return true;
		} else {
			apos = value.indexOf("@")
			dotpos = value.lastIndexOf(".")
			if (apos < 1 || dotpos - apos < 2) {
				return false;
			} else {
				return true;
			}
		}
	}
}

function validate_number(field){
	with (field) {	
		var exp = /^(\-)?\d*(\.\d+)?$/;
		if(!exp.test(value)) { 
			return false;
		}
	}
	
	return true;
}


function validate_required(field) {
	with (field) {
		if (value == null || value == "" || value == "default"){
			return false;
		} else {
			return true;
		}
	}
}


/*****************************************************************************************
/* Broker
*/

function selectBroker(value) {
	$("#message").html("");
	if(value == "default") {
		$('#mod_broker').hide();
		$('#add_broker').hide();
		return ;
	} else if(value == "add") {
		$('#mod_broker').hide();
		$('#add_broker').show();
	} else { 
    	Dajaxice.admins.getBroker(showBroker, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showBroker(data) {
	$('#mod_broker').hide();
	$('#add_broker').hide();
	
	if(data.success == "true") {
		$('#mod_broker').show();
		$('#mod_pk').val(data.pk);
		$('#mod_name').val(data.brokerNumber);
		$('#mod_type').val(data.securityType);
		$('#mod_commission').val(data.commissionRate);
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function validate_add_broker(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter a number.</span>";
			$("#add_name").after(html);
			add_name.focus();
			return false;
		} 
		if (validate_required(add_type) == false) {
			html = "<span class='help-inline message'>You must enter a type.</span>";
			$("#add_type").after(html);
			add_type.focus();
			return false;
		}
		if (validate_number(add_commission) == false || validate_required(add_commission) == false) {
			html = "<span class='help-inline message'>You must enter a valid commission.</span>";
			$("#add_commission").after(html);
			add_commission.focus();
			return false;
		}
	}
	return true
}

function validate_mod_broker(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_name) == false) {
			html = "<span class='help-inline message'>You must enter a number.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
			return false;
		} 
		
		if (validate_required(mod_type) == false) {
			html = "<span class='help-inline message'>You must enter a type.</span>";
			$("#mod_type").after(html);
			mod_type.focus();
			return false;
		}
		
		if (validate_number(mod_commission) == false || validate_required(mod_commission) == false) {
			html = "<span class='help-inline message'>You must enter a valid commission.</span>";
			$("#mod_commission").after(html);
			mod_commission.focus();
			return false;
		} 
	}
	return true
}

function confirm_delete_broker() {
	var result = confirm("Delete This Broker?")
  	return result;
}

/*****************************************************************************************
/* Trader
*/

function selectTrader(value) {
	$("#message").html("");
	$("#pills").find('li').removeClass("active");
	$("#pill"+value).addClass("active");
	
	// empty system checks
	$(".system_list").html("");
	$("input:checkbox[name=system]").each(function() {
         $(this).removeAttr('checked');
	});
	
	if(value == "default") {
		$('#mod_trader').hide();
		$('#add_trader').hide();
		return ;
	} else if(value == "add") {
		$('#mod_trader').hide();
		$('#add_trader').show();
	} else { 
    	Dajaxice.admins.getTrader(showTrader, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showTrader(data) {
	$('#mod_trader').hide();
	$('#add_trader').hide();
	if(data.success == "true") {
		$('#mod_trader').show();
		$('#mod_pk').val(data.pk);
		$('#mod_name').val(data.name);
		$('#mod_ssn').val(data.ssn);
		$('#mod_addr').val(data.addr);
		$('#mod_phone').val(data.phone);
		$('#mod_email').val(data.email);
		$('#mod_username').val(data.username);
		$('#mod_password').val(data.password);
		$('#mod_cfee').val(data.cfee.toFixed(2));
		$('#mod_bfee').val(data.bfee.toFixed(2));
		
		var number = data.system_list.length;
		$('.system_list').html("");
		var html = "";
		for(i = 0; i < number; i++) {
			var pk = data.system_list[i].pk;
			var system = data.system_list[i].fields;
			html += "<div class='system_tag' id='system_tag_"+pk+"'>";
			html += "<input name='systems' style='display:none' value='"+pk+"'>";
  			html += "<button type='button' class='close' data-dismiss='alert' onclick='removeSystem("+pk+")'>&times;</button>";
  			html += system.name;
			html += "</div>";
			$("#system"+pk).attr('checked','checked');
		}
		$('.system_list').append(html);

	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function validate_add_trader(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#add_name").after(html);
			add_name.focus();
			return false;
		} 
		if (validate_email(add_email) == false) {
			html = "<span class='help-inline message'>You must enter a valid email.</span>";
			$("#add_email").after(html);
			add_email.focus();
			return false;
		}
		if (validate_number(add_cfee) == false) {
			html = "<span class='help-inline message'>You must enter a valid clearance fee.</span>";
			$("#add_cfee").after(html);
			add_cfee.focus();
			return false;
		}
		if (validate_number(add_bfee) == false) {
			html = "<span class='help-inline message'>You must enter a valid broker fee.</span>";
			$("#add_bfee").after(html);
			add_bfee.focus();
			return false;
		}
	}
	return true
}

function validate_mod_trader(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
			return false;
		} 
		if (validate_email(mod_email) == false) {
			html = "<span class='help-inline message'>You must enter a valid email.</span>";
			$("#mod_email").after(html);
			mod_email.focus();
			return false;
		}
		if (validate_number(mod_cfee) == false) {
			html = "<span class='help-inline message'>You must enter a valid clearance fee.</span>";
			$("#mod_cfee").after(html);
			mod_cfee.focus();
			return false;
		}
		if (validate_number(mod_bfee) == false) {
			html = "<span class='help-inline message'>You must enter a valid broker fee.</span>";
			$("#mod_bfee").after(html);
			mod_bfee.focus();
			return false;
		}
	}
	return true
}

function confirm_delete_trader() {
	var result = confirm("Delete This Trader?")
  	return result;
}

/*****************************************************************************************
/* System
*/
function add_system() {
	$("#add_btn").hide();
	$("#add_system").show();
}

function confirm_delete_system() {
	var result = confirm("Delete This System?")
  	return result;
}

function validate_system(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(name) == false) {
			html = "<span class='help-inline message'>You must enter a valid system type.</span>";
			$("#system_list").after(html);
			name.focus();
			return false;
		} 
		if (validate_number(cost) == false || validate_required(cost) == false ) {
			html = "<span class='help-inline message'>You must enter a valid cost.</span>";
			$("#system_list").after(html);
			cost.focus();
			return false;
		}
	}
	return true
}

function getSystem() {
    var systemList = [];
	$("input:checkbox[name=system]:checked").each(function() {
         systemList.push($(this).val());
	});

	$(".system_list").html("");
	var html = "";
	for (i = 0; i < systemList.length; i++) {
		var pk = systemList[i];
		html += "<div class='system_tag' id='system_tag_"+pk+"'>";
		html += "<input name='systems' style='display:none' value='"+pk+"'>";
  		html += "<button type='button' class='close' data-dismiss='alert' onclick='removeSystem("+pk+")'>&times;</button>";
  		html += $("#type"+pk).html();
		html += "</div>"
	}
	$(".system_list").append(html);	
}

function removeSystem(pk) {
	var id = "system_tag_" + pk;
	$("#"+id).remove();
	$("#system"+pk).removeAttr('checked');
}

/*****************************************************************************************
/* Firm
*/

function validate_firm(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_number(equity) == false || validate_required(equity) == false ) {
			html = "<span class='help-inline message'>You must enter a valid number.</span>";
			$("#equity").after(html);
			equity.focus();
			return false;
		}
		if (validate_number(DVP) == false || validate_required(DVP) == false ) {
			html = "<span class='help-inline message'>You must enter a valid number.</span>";
			$("#DVP").after(html);
			DVP.focus();
			return false;
		}
		if (validate_number(options) == false || validate_required(options) == false ) {
			html = "<span class='help-inline message'>You must enter a valid number.</span>";
			$("#options").after(html);
			options.focus();
			return false;
		}
		if (validate_number(H2B) == false || validate_required(H2B) == false ) {
			html = "<span class='help-inline message'>You must enter a valid number.</span>";
			$("#H2B").after(html);
			H2B.focus();
			return false;
		}
		if (validate_number(secFee) == false || validate_required(secFee) == false ) {
			html = "<span class='help-inline message'>You must enter a valid number.</span>";
			$("#secFee").after(html);
			secFee.focus();
			return false;
		}
		if (validate_number(rent) == false || validate_required(rent) == false ) {
			html = "<span class='help-inline message'>You must enter a valid number.</span>";
			$("#rent").after(html);
			rent.focus();
			return false;
		}
	}
	return true
}

/*****************************************************************************************
/* Employer
*/

function selectEmployer(value) {
	$("#message").html("");
	$("#pills").find('li').removeClass("active");
	$("#pill"+value).addClass("active");
	
	if(value == "default") {
		$('#mod_employer').hide();
		$('#add_employer').hide();
		return ;
	} else if(value == "add") {
		$('#mod_employer').hide();
		$('#add_employer').show();
	} else { 
    	Dajaxice.admins.getEmployer(showEmployer, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showEmployer(data) {
	$('#mod_employer').hide();
	$('#add_employer').hide();
	if(data.success == "true") {
		$('#mod_employer').show();
		$('#mod_pk').val(data.pk);
		$('#mod_name').val(data.name);
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function validate_add_employer(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#add_name").after(html);
			add_name.focus();
			return false;
		} 
	}
	return true
}

function validate_mod_employer(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
			return false;
		} 
	}
	return true
}

function confirm_delete_employer() {
	var result = confirm("Delete This Employer?")
  	return result;
}

/*****************************************************************************************
/* FutureFeeRate
*/

function queryFutureList() { 
	$('#mod_future').hide();
	$('#add_future').hide();
    Dajaxice.admins.queryFutureList(createFutureList, {'symbol': $("#symbols").val()},
    							   				 	  {'error_callback': custom_error}); 		       
}

function showFutureList() {
	$("#symbols").val("");
	$('#mod_future').hide();
	$('#add_future').hide();
	Dajaxice.admins.showFutureList(createFutureList, {'error_callback': custom_error}); 
}

function createFutureList(data) {
	var number = data.future_list.length;
	$("#futures_container").empty(); // delete all the data
	$("#message_container").empty(); // delete all the data
	if(number == 0) {
		$("#futures_container").removeClass("container");
		var html = "";
		html += "No futures found.";
		$("#futures_container").append(html);
	} else {
		var html = "";
		
		html += "<ul class='nav nav-pills nav-stacked' id='futurepills'>";
				
		for(i = 0; i < number; i++) { // create a new list of reports
			var pk = data.future_list[i].pk;
			var future = data.future_list[i].fields;
			var group = "";
			
			if (future.group == "HigherFeeRate") {
				group = "Higher";
			} else {
				group = "Lower";
			}
			
			html += "<li id='pill" + pk + "'><a class='btn-link' onclick='selectFuture(" + pk + ")'>" 
			+ future.symbol + " " + group + "</a></li>";
		}
		
		html += "</ul>";
		
		$("#futures_container").addClass("container");
		$("#futures_container").append(html);
    }
}

function selectFuture(value) {
	$("#message").html("");
	$("#pills").find('li').removeClass("active");
	$("#futurepills").find('li').removeClass("active");
	$("#pill"+value).addClass("active");
	
	if(value == "default") {
		$('#mod_future').hide();
		$('#add_future').hide();
		return ;
	} else if(value == "add") {
		$('#mod_future').hide();
		$('#add_future').show();
	} else { 
    	Dajaxice.admins.getFuture(showFuture, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showFuture(data) {
	$('#mod_future').hide();
	$('#add_future').hide();
	if(data.success == "true") {
		$('#mod_future').show();
		$('#mod_pk').val(data.pk);
		$('#mod_symbol').val(data.symbol);
		$('#mod_clearing').val(data.clearing.toFixed(4));
		$('#mod_exchange').val(data.exchange.toFixed(4));
		$('#mod_nfa').val(data.nfa.toFixed(4));
		$('#mod_group').val(data.group)
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function validate_add_future(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_symbol) == false) {
			html = "<span class='help-inline message'>You must enter a symbol.</span>";
			$("#add_symbol").after(html);
			add_symbol.focus();
			return false;
		} 
		if (validate_required(add_clearing) == false || validate_number(add_clearing) == false) {
			html = "<span class='help-inline message'>You must enter a valid clearance fee rate.</span>";
			$("#add_clearing").after(html);
			add_clearing.focus();
			return false;
		}
		if (validate_required(add_exchange) == false || validate_number(add_exchange) == false) {
			html = "<span class='help-inline message'>You must enter a valid exchange fee rate.</span>";
			$("#add_exchange").after(html);
			add_exchange.focus();
			return false;
		}
		if (validate_required(add_nfa) == false || validate_number(add_nfa) == false) {
			html = "<span class='help-inline message'>You must enter a valid nfa fee rate.</span>";
			$("#add_nfa").after(html);
			add_nfa.focus();
			return false;
		}
	}
	return true
}

function validate_mod_future(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_symbol) == false) {
			html = "<span class='help-inline message'>You must enter a symbol.</span>";
			$("#mod_symbol").after(html);
			mod_symbol.focus();
			return false;
		} 
		if (validate_required(mod_clearing) == false || validate_number(mod_clearing) == false) {
			html = "<span class='help-inline message'>You must enter a valid clearance fee rate.</span>";
			$("#mod_clearing").after(html);
			mod_clearing.focus();
			return false;
		}
		if (validate_required(mod_exchange) == false || validate_number(mod_exchange) == false) {
			html = "<span class='help-inline message'>You must enter a valid exchange fee rate.</span>";
			$("#mod_exchange").after(html);
			mod_exchange.focus();
			return false;
		}
		if (validate_required(mod_nfa) == false || validate_number(mod_nfa) == false) {
			html = "<span class='help-inline message'>You must enter a valid nfa fee rate.</span>";
			$("#mod_nfa").after(html);
			mod_nfa.focus();
			return false;
		}
	}
	return true
}

function confirm_delete_future() {
	var result = confirm("Delete This Future?")
  	return result;
}

/*****************************************************************************************
/* FutureFeeGroup
*/

function validate_feeGroup(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(symbols) == false) {
			html = "<span class='help-block message'>You must select a symbol.</span>";
			$("#symbols").after(html);
			return false;
		} 
		if (validate_required(accounts) == false) {
			html = "<span class='help-block message'>You must select an account.</span>";
			$("#accounts").after(html);
			return false;
		}
		if (validate_required(groups) == false) {
			html = "<span class='help-block message'>You must select a group.</span>";
			$("#groups").after(html);
			return false;
		}
	}
	return true
}

function selectFeeGroup() {
	var symbol = $("#symbols").val();
	var account = $("#accounts").val();
	var group = $("#groups").val();
	
	Dajaxice.admins.getFeeGroup(showFeeGroup, {'symbol': symbol, 'account': account, 'group': group},
							 	{'error_callback': custom_error}); 
}

function showFeeGroup(data) {
	$("#feegroup_container").empty(); // delete all the data
	
	if (data.success == "false") {
		$("#feegroup_container").removeClass("container");
		var html = data.message;
		$("#feegroup_container").append(html);
	} else {	
		var number = data.feeGroupList.length;
		
		// one account should be in only one group for one symbol
		if (data.existed == "true") {
			$("#add").attr("disabled", true);
		} else if ($("#add").attr("disabled", true)) {
			$("#add").removeAttr("disabled");
		}
		
		if(number == 0) {
			$("#feegroup_container").removeClass("container");
			var html = "";
			$("#feegroup_container").append(html);
		} else {
			var html = "";
			//var csrf = $.cookie('csrftoken');
			
			html += "<table class='table group_table table-bordered'>";
			for(i = 0; i < number; i++) { // create a new list of reports
				var feegroup = data.feeGroupList[i].fields;
				html += "<form method='post' action='/modFeeGroup/' onsubmit='return validate_feeGroup(this)'>";
				//html += csrf;
				html += "<tr>";
				html += "<td>" + feegroup.symbol;
				html += "<input type='hidden' name='symbols' value='" + feegroup.symbol + "'/></td>";
				html += "<td>" + feegroup.account;
				html += "<input type='hidden' name='accounts' value='" + feegroup.account + "'/></td>";
				
				html += "<td>" + "<select  id='groups' name = 'groups' size = '1' style = 'padding-bottom:20px;margin-top:10px;width:180px'>";
				html +=	"<option value=" + feegroup.group + ">" + feegroup.group + "</option>";				
				for (j = 0; j < data.groupList.length; j++) {
					var group = data.groupList[j].fields;
					
					if (group.name != feegroup.group) {
						html += "<option value=" + group.name + ">" + group.name + "</option>";
					}
				}
				html += "</select></td>";
				
				html += "<td><input type='submit' name='save' class='btn btn-info' value='Save'>";
				html += "<input type='submit' name='delete' class='btn btn-danger' value='Delete' style='margin-left:5px;'" +
						"onclick='return confirm_delete_feeGroup()'></td>";
				html += "</tr>";
				html += "</form>";
			}
			
			html += "</table>";
			
			$("#feegroup_container").addClass("container");
			$("#feegroup_container").append(html);
	    }
	}
}

function confirm_delete_feeGroup() {
	var result = confirm("Delete This Future Group Record?")
  	return result;
}

/*****************************************************************************************
/* Account
*/

function selectAccount(value) {
	$("#message").html("");
	$("#pills").find('li').removeClass("active");
	$("#accountpills").find('li').removeClass("active");
	$("#pill"+value).addClass("active");
	
	if(value == "default") {
		$('#mod_account').hide();
		$('#add_account').hide();
		return ;
	} else if(value == "add") {
		$('#mod_account').hide();
		$('#add_account').show();
	} else { 
    	Dajaxice.admins.getAccount(showAccount, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showAccount(data) {
	$('#mod_account').hide();
	$('#add_account').hide();
	if(data.success == "true") {
		$('#mod_account').show();
		$('#mod_pk').val(data.pk);
		$('#mod_name').val(data.account);
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function validate_add_account(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter an account name.</span>";
			$("#add_name").after(html);
			add_name.focus();
			return false;
		} else {
			var account = $("#add_name").val();
			var ret = true;
			$("a[class='account']").each(function(){
				if( $(this).html() == account ) {
					html = "<span class='help-inline message'>Account already exists.</span>";
					$("#add_name").after(html);
					add_name.focus();
					ret = false;
				}
			});
			return ret;
		}
	}
	return true
}

function validate_mod_account(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_name) == false) {
			html = "<span class='help-inline message'>You must enter an account name.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
			return false;
		} /* else {
			var account = $("#mod_name").val();
			var ret = true;
			$("a[class='account']").each(function(){
				if( $(this).html() == account ) {
					html = "<span class='help-inline message'>Account already exists.</span>";
					$("#mod_name").after(html);
					mod_name.focus();
					ret = false;
				}
			});
			return ret;
		} */
	}
	return true
}

function confirm_delete_account() {
	var result = confirm("Delete This Account?")
  	return result;
}


/*****************************************************************************************
/* Group
*/

function selectGroup(value) {
	$("#message").html("");
	$("#pills").find('li').removeClass("active");
	$("#pill"+value).addClass("active");
	
	if(value == "default") {
		$('#mod_group').hide();
		$('#add_group').hide();
		return ;
	} else if(value == "add") {
		$('#mod_group').hide();
		$('#add_group').show();
	} else { 
    	Dajaxice.admins.getGroup(showGroup, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showGroup(data) {
	$('#mod_group').hide();
	$('#add_group').hide();
	if(data.success == "true") {
		$('#mod_group').show();
		$('#mod_pk').val(data.pk);
		$('#mod_name').val(data.name);
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function validate_add_group(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter a group name.</span>";
			$("#add_name").after(html);
			add_name.focus();
			return false;
		}
	}
	return true
}

function validate_mod_group(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_name) == false) {
			html = "<span class='help-inline message'>You must enter a group name.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
			return false;
		}
	}
	return true
}

function confirm_delete_group() {
	var result = confirm("Delete This Group?")
  	return result;
}
