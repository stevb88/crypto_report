
### Crypto Report and Analysis

This simple script (for italian spoken users) is an exercise prepared for a Start2Impact guide project.

The script needs the BCpython module (whose description is in the module itself) to run and a CoinMarketCap API key to get the data (if you don't have one you can get it for free from [CMC signup](https://pro.coinmarketcap.com/signup)).

The script allows the scheduling of a recursive creation of two kind of report: one .json file containing the db downloaded from CMC (saved in a 'Raw Data' folder), one .txt file with some user friendly kind data about cryptovalues (saved in a 'Reports' folder). While scheduling your report you can choose:
+ the currency in which you want to express the values (default: USD),
+ the main folder in which you want to save reports (default: 'Report', will be create in the current path),
+ scheduling interval (default: 24h),
+ when you want to start mining data (default: now).

The .txt report is in italian and answer the following question:
+ best cryptos by volume in the last 24h,
+ best and worst 10 cryptos in the last 24h,
+ the money you need to buy one of the best 20 cryptos by market cap,
+ the money you need to buy one of alle the cryptos with a 24h volume exchange more than 76.000.000 of the currency you choose,
+ the % change you should have got if you bought yesterday the 20 best cryptos by market cap.

While this recursive analysis run, user can mine and read on the screen some interesting data on cryptovalues (both from the last .json db saved or from fresh data from CMC).
+ prices,
+ volume,
+ market cap,
+ market dominance,
+ % change during the last hour,
+ % change during the last 24 hour,
+ % change during the last 7 days,
+ % change during the last 30 days,
+ % change during the last 60 days,
+ % change during the last 90 days.

User can decide to filter the data or not (greater or less than a threshold), to print it sorted in ascending or descending order, to get it from the last scheduled download or from the last updated data.
