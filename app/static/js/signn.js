$(document).ready(function(){
	$("button").click(function(){
		$("h1").hide();
	});
});


$(document).ready(function(){
	$("p").mouseenter(function(){
		$("p").hide();
	});
});

// $(document).ready(function(){
// 	$("form").submit(function(e){
// 		var url = "{{ url_for('something') }}";
// 		$.ajax({
// 			type: "POST",
// 			url: url,
// 			data: $('form').serialize(),
// 			success: function(data){
// 				console.log(data)
// 			}
// 		});
// 		e.preventDefault();
// 	});
// });
