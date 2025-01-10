	
 $(document).ready(function(){
		$('.slider-div').owlCarousel({
		loop: true,
		margin:30,
		autoplay:true,
		nav:false,
		dots: true,
        dotsData: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		
		  1200: {
			items:1
		  }
	  
		}
	  })



	  $('.best-slider').owlCarousel({
		loop: true,
		margin:50,
		autoplay:true,
		nav:false,
		dots: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		  667: {
			items:2
		  },
		  1024: {
			items:3
		  },
		  1200: {
			items:3
		  }
	  
		}
	  })


	  $('.tser-slider01').owlCarousel({
		loop: true,
		margin:50,
		autoplay:true,
		nav:false,
		dots: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		  768: {
			items:2
		  },
		  1200: {
			items:3
		  }
	  
		}
	  })


	  $('.slider-texr').owlCarousel({
		loop: true,
		margin:50,
		autoplay:true,
		nav:false,
		dots: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		  667: {
			items:2
		  },
		  768: {
			items:3
		  },
		  1200: {
			items:4
		  }
	  
		}
	  })



	  $('.client-slider').owlCarousel({
		loop: true,
		margin:30,
		autoplay:true,
		nav:false,
		dots: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		
		  1200: {
			items:5
		  }
	  
		}
	  })



	  $('.slio-eveny').owlCarousel({
		loop: true,
		margin:30,
		autoplay:true,
		nav:false,
		dots: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		  667: {
			items:2
		  },
		  1024: {
			items:3
		  },
		  1200: {
			items:3
		  }
	  
		}
	  })


	  $('.shop-slider').owlCarousel({
		loop: true,
		margin:30,
		autoplay:true,
		nav:false,
		dots: true,
		responsive: {
		  0: {
			items:1
		  },
		  375: {
			items:1
		  },
		  600: {
			  items:1
		  },
		  667: {
			items:2
		  },
		  1024: {
			items:3
		  },

		  1200: {
			items:4
		  }
	  
		}
	  })
	  
	  
	  
	  
  
});


$(document).ready(function() {
    $( window ).scroll(function() {
          var height = $(window).scrollTop();
          if(height >= 100) {
              $('header').addClass('fixed-menu');
          } else {
              $('header').removeClass('fixed-menu');
          }
      });
});

$(document).ready(function(){
	$(".radiou").slice(0, 6).show();
	$(".load-more").click(function(e){
		e.preventDefault();
		$(".radiou:hidden").slice(0, 3).slideDown();
		if ($(".radiou:hidden").length == 0) {
			$(".load-more").fadeOut("slow");
		}
	});


	// Показываем первые 12 товаров при загрузке страницы
    $(".collist").slice(0, 12).show();

    // Проверяем, есть ли больше 12 товаров и скрываем остальные
    if ($(".collist").length > 12) {
        $(".collist").slice(12).hide();
    }

    // Обработчик для кнопки "Load More"
    $(".load-more3").click(function (e) {
        e.preventDefault();

        // Показываем еще по 4 товара при каждом клике
        $(".collist:hidden").slice(0, 4).slideDown();

        // Если скрытых товаров больше нет, скрываем кнопку "Load More"
        if ($(".collist:hidden").length === 0) {
            $(".load-more3").fadeOut("slow");
        }
    });

	
});


$(document).ready(function(){
	function getVals(){
		// Get slider values
		let parent = this.parentNode;
		let slides = parent.getElementsByTagName("input");
		let slide1 = parseFloat( slides[0].value );
		let slide2 = parseFloat( slides[1].value );
		// Neither slider will clip the other, so make sure we determine which is larger
		if( slide1 > slide2 ){ let tmp = slide2; slide2 = slide1; slide1 = tmp; }
		
		let displayElement = parent.getElementsByClassName("rangeValues")[0];
			displayElement.innerHTML = "$" + slide1 + " - $" + slide2;
	}
	
	window.onload = function(){
		// Initialize Sliders
		let sliderSections = document.getElementsByClassName("range-slider");
			for( let x = 0; x < sliderSections.length; x++ ){
			let sliders = sliderSections[x].getElementsByTagName("input");
			for( let y = 0; y < sliders.length; y++ ){
				if( sliders[y].type ==="range" ){
				sliders[y].oninput = getVals;
				// Manually trigger event first time to display values
				sliders[y].oninput();
				}
			}
			}
	}
});

// dropdown

$(document).ready(function(){

	$(".custom-select").each(function() {
	  var classes = $(this).attr("class"),
		id      = $(this).attr("id"),
		name    = $(this).attr("name");
	  var template =  '<div class="' + classes + '">';
		template += '<span class="custom-select-trigger">' + $(this).attr("name") + '</span>';
		template += '<div class="custom-options">';
		$(this).find("option").each(function() {
		  template += '<span class="custom-option ' + $(this).attr("class") + '" data-value="' + $(this).attr("value") + '">' + $(this).html() + '</span>';
		});
	  template += '</div></div>';
	  
	  $(this).wrap('<div class="custom-select-wrapper"></div>');
	  $(this).hide();
	  $(this).after(template);
	  });
	  $(".custom-option:first-of-type").hover(function() {
	  $(this).parents(".custom-options").addClass("option-hover");
	  }, function() {
	  $(this).parents(".custom-options").removeClass("option-hover");
	  });
	  $(".custom-select-trigger").on("click", function() {
	  $('html').one('click',function() {
		$(".custom-select").removeClass("opened");
	  });
	  $(this).parents(".custom-select").toggleClass("opened");
	  event.stopPropagation();
	  });
	  $(".custom-option").on("click", function() {
	  $(this).parents(".custom-select-wrapper").find("select").val($(this).data("value"));
	  $(this).parents(".custom-options").find(".custom-option").removeClass("selection");
	  $(this).addClass("selection");
	  $(this).parents(".custom-select").removeClass("opened");
	  $(this).parents(".custom-select").find(".custom-select-trigger").text($(this).text());
	  });
	
});


// products slide

$(document).ready(function () {
	var sync1 = $("#sync1");
	var sync2 = $("#sync2");
	var slidesPerPage = 3; //globaly define number of elements per page
	var syncedSecondary = true;
  
	sync1
	  .owlCarousel({
		items: 1,
		slideSpeed: 2000,
		nav: false,
		autoplay: false,
		dots: false,
		loop: true,
		responsiveRefreshRate: 200,
		
	  })
	  .on("changed.owl.carousel", syncPosition);
  
	sync2
	  .on("initialized.owl.carousel", function () {
		sync2.find(".owl-item").eq(0).addClass("current");
	  })
	  .owlCarousel({
		items: slidesPerPage,
		dots: true,
		nav: false,
		smartSpeed: 200,
		slideSpeed: 500,
		slideBy: slidesPerPage, //alternatively you can slide by 1, this way the active slide will stick to the first item in the second carousel
		responsiveRefreshRate: 100
	  })
	  .on("changed.owl.carousel", syncPosition2);
  
	function syncPosition(el) {
	  //if you set loop to false, you have to restore this next line
	  //var current = el.item.index;
  
	  //if you disable loop you have to comment this block
	  var count = el.item.count - 1;
	  var current = Math.round(el.item.index - el.item.count / 2 - 0.5);
  
	  if (current < 0) {
		current = count;
	  }
	  if (current > count) {
		current = 0;
	  }
  
	  //end block
  
	  sync2
		.find(".owl-item")
		.removeClass("current")
		.eq(current)
		.addClass("current");
	  var onscreen = sync2.find(".owl-item.active").length - 1;
	  var start = sync2.find(".owl-item.active").first().index();
	  var end = sync2.find(".owl-item.active").last().index();
  
	  if (current > end) {
		sync2.data("owl.carousel").to(current, 100, true);
	  }
	  if (current < start) {
		sync2.data("owl.carousel").to(current - onscreen, 100, true);
	  }
	}
  
	function syncPosition2(el) {
	  if (syncedSecondary) {
		var number = el.item.index;
		sync1.data("owl.carousel").to(number, 100, true);
	  }
	}
  
	sync2.on("click", ".owl-item", function (e) {
	  e.preventDefault();
	  var number = $(this).index();
	  sync1.data("owl.carousel").to(number, 300, true);
	});
  });


  //  size js
$(document).ready(function () {
	var selector = '.sixe-menu-q li';
	
	  $(selector).on('click', function(){
		  $(selector).removeClass('active');
		  $(this).addClass('active');
	  });
});
  
  


// quantity js

// quantity
(function () {
    "use strict";
    var jQueryPlugin = (window.jQueryPlugin = function (ident, func) {
      return function (arg) {
        if (this.length > 1) {
          this.each(function () {
            var $this = $(this);
  
            if (!$this.data(ident)) {
              $this.data(ident, func($this, arg));
            }
          });
  
          return this;
        } else if (this.length == 1) {
          if (!this.data(ident)) {
            this.data(ident, func(this, arg));
          }
  
          return this.data(ident);
        }
      };
    });
  })();
  
  (function () {
    "use strict";
    function Guantity($root) {
      const element = $root;
      const quantity = $root.first("data-quantity");
      const quantity_target = $root.find("[data-quantity-target]");
      const quantity_minus = $root.find("[data-quantity-minus]");
      const quantity_plus = $root.find("[data-quantity-plus]");
      var quantity_ = quantity_target.val();
      $(quantity_minus).click(function () {
        quantity_target.val(--quantity_);
      });
      $(quantity_plus).click(function () {
        quantity_target.val(++quantity_);
      });
    }
    $.fn.Guantity = jQueryPlugin("Guantity", Guantity);
    $("[data-quantity]").Guantity();
  })();