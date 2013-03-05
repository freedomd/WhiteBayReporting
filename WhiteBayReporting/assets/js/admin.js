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
		if (value == null || value == ""){
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
		$('#mod_name').val(data.name);
		$('#mod_commission').val(data.commission.toFixed(2));
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function modifyBroker() {
	Dajaxice.admins.modifyBroker(showBroker, {'pk': value}, {'error_callback': custom_error});
}

function validate_add_broker(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#add_name").after(html);
			add_name.focus();
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
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
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

