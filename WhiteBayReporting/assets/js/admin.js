function custom_error(){
    // do nothing
}

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
    	Dajaxice.brokers.getBroker(showBroker, {'pk': value}, {'error_callback': custom_error}); 		
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
	Dajaxice.brokers.modifyBroker(showBroker, {'pk': value}, {'error_callback': custom_error});
}


function validate_number(field){
	with (field) {
		if (value == null || value == "") {
			return false;
		}
				
		var exp = /^(\-)?\d+(\.\d+)?$/;
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

function validate_add(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#add_name").after(html);
			add_name.focus();
			return false;
		} 
		if (validate_number(add_commission) == false) {
			html = "<span class='help-inline message'>You must enter a valid commission.</span>";
			$("#add_commission").after(html);
			add_commission.focus();
			return false;
		}
	}
	return true
}

function validate_mod(thisform) {
	$(".message").html("");
	with (thisform) {
		if (validate_required(mod_name) == false) {
			html = "<span class='help-inline message'>You must enter a name.</span>";
			$("#mod_name").after(html);
			mod_name.focus();
			return false;
		} 
		
		if (validate_number(mod_commission) == false) {
			html = "<span class='help-inline message'>You must enter a valid commission.</span>";
			$("#mod_commission").after(html);
			mod_commission.focus();
			return false;
		} 
	}
	return true
}

function confirm_delete() {
	var result = confirm("Delete This Broker?")
  	return result;
}

