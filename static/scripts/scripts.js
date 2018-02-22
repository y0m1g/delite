$( function() {

	// Brightness
	$( "#bright" ).slider({
		orientation: "horizontal",
      	range: "min",
		max: 255,
		value: 127,
		slide: function( event, ui ) {
			$.post( "/brightness", { "value": ui.value } );
		}
  });
  $.get( "/brightness", function (value) {
      $( "#bright" ).slider( "value", value )
    } 
  );
	
	// Color sliders
  function hexFromRGB(r, g, b) {
    var hex = [
      r.toString( 16 ),
      g.toString( 16 ),
      b.toString( 16 )
    ];
    $.each( hex, function( nr, val ) {
      if ( val.length === 1 ) {
        hex[ nr ] = "0" + val;
      }
    });
    return hex.join( "" ).toUpperCase();
  }
  function refreshColor() {
    var red = $( "#red" ).slider( "value" ),
      green = $( "#green" ).slider( "value" ),
      blue = $( "#blue" ).slider( "value" ),
      hex = hexFromRGB( red, green, blue );
    $.post( "/color", { "r": red, "g": green, "b": blue } );
	  $( "#swatch" ).css( "background-color", "#" + hex );
  }
  $( "#red, #green, #blue" ).slider({
    orientation: "horizontal",
    range: "min",
    max: 255,
    value: 127,
    slide: refreshColor,
    change: refreshColor
  });
  
  // Presets
  $( "#turnon" ).on( "click", function() {
    $.post( "/preset", { "value": "on" } );
  });
  $( "#turnoff" ).on( "click", function() {
    $.post( "/preset", { "value": "off" } );
  });
  $( "#sunset" ).on( "click", function() {
    $.post( "/preset", { "value": "sunset" } );
  });
  $( "#sunrise" ).on( "click", function() {
    $.post( "/preset", { "value": "sunrise" } );
  });

} );