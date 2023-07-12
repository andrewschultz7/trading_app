// import { useEffect, useState, useRef, useMemo } from 'react';
// import './App.css';
// import Chart from 'react-apexcharts';

// async function getStonks(): Promise<any> {
//   const stonksUrl = `http://localhost:8080/historical`;
//   const response = await fetch(stonksUrl);
//   return response.json();
// }

// const directionEmojis = {
//   up: '🚀',
//   down: '🔻',
//   '': '',
// };

// function App() {
//   const chartRef = useRef(null);
//   const [series, setSeries] = useState([]);
//   const [price, setPrice] = useState(-1);
//   const [prevPrice, setPrevPrice] = useState(-1);
//   const [priceTime, setPriceTime] = useState(null);
//   const [annotations, setAnnotations] = useState([]);

//   useEffect(() => {
//     let timeoutId;

//     async function getLatestPrice() {
//       try {
//         const data = await getStonks();
//         const prices = data.map((item) => ({
//           x: new Date(item.Datetime),
//           y: [item.Open, item.High, item.Low, item.Close],
//         }));

//         const latestPrice = parseFloat(prices[prices.length - 1].y[3]);
//         setPrevPrice(price);
//         setPrice(latestPrice);
//         setPriceTime(new Date(prices[prices.length - 1].x));
//         setSeries([{ data: prices }]);
//       } catch (error) {
//         console.log(error);
//       }

//       timeoutId = setTimeout(getLatestPrice, 5000 * 2);
//     }

//     getLatestPrice();

//     return () => {
//       clearTimeout(timeoutId);
//     };
//   }, []);

//   const direction = useMemo(() => {
//     if (prevPrice < price) {
//       return 'up';
//     } else if (prevPrice > price) {
//       return 'down';
//     } else {
//       return '';
//     }
//   }, [prevPrice, price]);

//   const handleChartClick = ({ dataPointIndex }) => {
//     if (chartRef.current) {
//       const annotationText = `Annotation ${annotations.length + 1}`;
//       const chart = chartRef.current.chart;
//       const series = chart.w.globals.series[0];
//       const dataItem = series[dataPointIndex];

//       const annotation = {
//         x: dataItem.x,
//         y: dataItem.y[3],
//         marker: {
//           size: 4,
//           fillColor: '#ff0000',
//           strokeColor: '#fff',
//           radius: 2,
//         },
//         label: {
//           borderColor: '#ff0000',
//           style: {
//             color: '#fff',
//             background: '#ff0000',
//           },
//           text: annotationText,
//           offsetY: -15,
//         },
//       };

//       chart.addPointAnnotation(annotation);
//       setAnnotations([...annotations, annotation]);
//     }
//   };

//   const chartOptions = {
//     chart: {
//       type: 'candlestick',
//       height: 350,
//       events: {
//         click: handleChartClick,
//       },
//     },
//     series: [],
//     title: {
//       text: 'CandleStick Chart',
//       align: 'left',
//     },
//     xaxis: {
//       type: 'datetime',
//     },
//     yaxis: {
//       tooltip: {
//         enabled: true,
//       },
//     },
//     annotations: {
//       points: annotations,
//     },
//   };

//   return (
//     <div>
//       <div className="ticker">Sample Data</div>
//       <div className={['price', direction].join(' ')}>
//         ${price} {directionEmojis[direction]}
//       </div>
//       <div className="price-time">{priceTime && priceTime.toLocaleTimeString()}</div>
//       <Chart
//         options={chartOptions}
//         series={series}
//         type="candlestick"
//         width="100%"
//         height={320}
//         ref={chartRef}
//       />
//     </div>
//   );
// }

// export default App;

import { useEffect, useState, useRef, useMemo } from 'react';
import './App.css';
import Chart from 'react-apexcharts';

const directionEmojis = {
  up: '🚀',
  down: '🔻',
  '': '',
};

const initialAnnotations = [
  {
    x: new Date('2023-06-05T01:00:00.000Z').getTime(),
    y: 4288,
    marker: {
      size: 4,
      fillColor: '#ff0000',
      strokeColor: '#fff',
      radius: 2,
    },
    label: {
      borderColor: '#ff0000',
      style: {
        color: '#fff',
        background: '#ff0000',
      },
      text: 'Annotation 1',
      offsetY: -30,
    },
  },
  {
    x: new Date('2023-06-05T05:05:00.000Z').getTime(),
    y: 4286.5,
    marker: {
      size: 4,
      fillColor: '#00ff00',
      strokeColor: '#fff',
      radius: 2,
    },
    label: {
      borderColor: '#00ff00',
      style: {
        color: '#fff',
        background: '#00ff00',
      },
      text: 'Annotation 2',
      offsetY: -60,
    },
  },
];

const chartOptions = {
  chart: {
    type: 'candlestick',
    height: 350,
  },
  series: [],
  title: {
    text: 'CandleStick Chart',
    align: 'left',
  },
  xaxis: {
    type: 'datetime',
  },
  yaxis: {
    tooltip: {
      enabled: true,
    },
  },
  annotations: {
    points: initialAnnotations,
  },
};

const App = () => {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState({
    series: [],
    price: -1,
    prevPrice: -1,
    priceTime: null,
    annotations: initialAnnotations,
  });

  const fetchData = useCallback(async () => {
    try {
      const stonksUrl = `http://localhost:8080/historical`;
      const response = await fetch(stonksUrl);
      const data = await response.json();

      const prices = data.map((item) => ({
        x: new Date(item.Datetime).getTime(),
        y: [item.Open, item.High, item.Low, item.Close],
      }));

      const latestPrice = parseFloat(prices[prices.length - 1].y[3]);

      setChartData((prevChartData) => ({
        ...prevChartData,
        prevPrice: prevChartData.price !== latestPrice ? latestPrice : prevChartData.prevPrice,
        price: latestPrice,
        priceTime: new Date(prices[prices.length - 1].x),
        series: [{ data: prices }],
      }));
    } catch (error) {
      console.log(error);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000 * 2);

    return () => {
      clearInterval(interval);
    };
  }, [fetchData]);

  const handleChartClick = useCallback(({ dataPointIndex }) => {
    if (chartRef.current) {
      const annotationText = `Annotation ${chartData.annotations.length + 1}`;
      const chart = chartRef.current.chart;
      const series = chart.w.globals.series[0];
      const dataItem = series[dataPointIndex];

      const offsetY = -30 * chartData.annotations.length;

      const annotation = {
        x: dataItem.x,
        y: dataItem.y[3],
        marker: {
          size: 4,
          fillColor: '#ff0000',
          strokeColor: '#fff',
          radius: 2,
        },
        label: {
          borderColor: '#ff0000',
          style: {
            color: '#fff',
            background: '#ff0000',
          },
          text: annotationText,
          offsetY,
        },
      };

      chart.addPointAnnotation(annotation);
      setChartData((prevChartData) => ({
        ...prevChartData,
        annotations: [...prevChartData.annotations, annotation],
      }));
    }
  }, [chartData.annotations]);

  const direction = chartData.prevPrice < chartData.price ? 'up' : chartData.prevPrice > chartData.price ? 'down' : '';

  return (
    <div>
      <div className="ticker">Sample Data</div>
      <div className={`price ${direction}`}>
        ${chartData.price} {directionEmojis[direction]}
      </div>
      <div className="price-time">{chartData.priceTime && chartData.priceTime.toLocaleTimeString()}</div>
      <Chart
        options={chartOptions}
        series={chartData.series}
        type="candlestick"
        width="100%"
        height={320}
        ref={chartRef}
      />
    </div>
  );
};

export default App;
