import { useEffect, useState, useMemo } from 'react';
import "./App.css"
import Chart from 'react-apexcharts';


async function getStonks(): Promise<any> {
  const stonksUrl = `https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo`;
  const response = await fetch(stonksUrl);
  console.log(response);
  return response.json();
}

const directionEmojis = {
  up: '🚀',
  down: '💩',
  '': '',
};

const chart = {
  options: {
    chart: {
      type: 'candlestick',
      height: 350
    },
    series: [], // Add the series property here
    title: {
      text: 'CandleStick Chart',
      align: 'left'
    },
    xaxis: {
      type: 'datetime'
    },
    yaxis: {
      tooltip: {
        enabled: true
      }
    }
  },
};



function App() {
  const [series, setSeries] = useState([]);
  const [price, setPrice] = useState(-1);
  const [prevPrice, setPrevPrice] = useState(-1);
  const [priceTime, setPriceTime] = useState(null);

  useEffect(() => {
    let timeoutId;

    async function getLatestPrice() {
      try {
        const data = await getStonks();
        console.log(data);

        const quote = data['Time Series (5min)'];
        const prices = Object.entries(quote).map(([timestamp, values]) => ({
          x: new Date(timestamp),
          y: [
            parseFloat(values['1. open']),
            parseFloat(values['2. high']),
            parseFloat(values['3. low']),
            parseFloat(values['4. close']),
          ],
        }));

        const latestPrice = parseFloat(prices[prices.length - 1].y[3]);
        setPrevPrice(price);
        setPrice(latestPrice);
        setPriceTime(new Date(prices[prices.length - 1].x));
        setSeries([{ data: prices }]);
      } catch (error) {
        console.log(error);
      }

      timeoutId = setTimeout(getLatestPrice, 5000 * 2);
    }

    getLatestPrice();

    return () => {
      clearTimeout(timeoutId);
    };
  }, []);

  const direction = useMemo(() => {
    if (prevPrice < price) {
      return 'up';
    } else if (prevPrice > price) {
      return 'down';
    } else {
      return '';
    }
  }, [prevPrice, price]);

  return (
    <div>
      <div className="ticker">Sample Data</div>
      <div className={['price', direction].join(' ')}>
        ${price} {directionEmojis[direction]}
      </div>
      <div className="price-time">{priceTime && priceTime.toLocaleTimeString()}</div>
      <Chart options={chart.options} series={series} type="candlestick" width="100%" height={320} />
    </div>
  );
}


export default App;
