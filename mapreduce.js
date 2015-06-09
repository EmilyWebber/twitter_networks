// Functions for MongoDB MapReduce
//
var map = function() {
	// Find character count per tweet
 	var tweets = this.text;
 	var tweetChar = tweets.split("");
 	var charCount = tweetChar.length;
 	emit(charCount, 1)
 	}

var reduce = function(key, values) {
 	var count = 0;
 	// Count the number of tweets with a given character count
 	values.forEach(function(v) {
 		count += v;
 		})
	return count
 	}

//db.blacklivesmatter.mapReduce(map, reduce, {out: "char_count"})
