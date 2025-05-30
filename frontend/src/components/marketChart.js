import React, { useEffect, useRef } from "react";

const MarketChart = () => {
  const miniWidgetRef = useRef(null);
  const timelineWidgetRef = useRef(null);

  useEffect(() => {
    // Clear existing content before injecting new scripts
    if (miniWidgetRef.current) miniWidgetRef.current.innerHTML = "";
    if (timelineWidgetRef.current) timelineWidgetRef.current.innerHTML = "";

    // Mini Symbol Overview widget
    const miniScript = document.createElement("script");
    miniScript.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js";
    miniScript.async = true;
    miniScript.innerHTML = JSON.stringify({
      symbol: "AMEX:SPY",
      width: 350,
      height: 150,
      locale: "en",
      dateRange: "12M",
      colorTheme: "light",
      isTransparent: false,
      autosize: false,
      largeChartUrl: "",
    });

    if (miniWidgetRef.current) miniWidgetRef.current.appendChild(miniScript);

    // Timeline widget
    const timelineScript = document.createElement("script");
    timelineScript.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-timeline.js";
    timelineScript.async = true;
    timelineScript.innerHTML = JSON.stringify({
      feedMode: "all_symbols",
      isTransparent: false,
      displayMode: "regular",
      width: 300,
      height: 350,
      colorTheme: "light",
      locale: "en",
    });

    if (timelineWidgetRef.current)
      timelineWidgetRef.current.appendChild(timelineScript);

    // Cleanup on unmount
    return () => {
      if (miniWidgetRef.current) miniWidgetRef.current.innerHTML = "";
      if (timelineWidgetRef.current) timelineWidgetRef.current.innerHTML = "";
    };
  }, []);

  return (
    <nav id="tradingview" className="flex flex-col gap-6">
      <div className="tradingview-widget-container" ref={miniWidgetRef}></div>
      <div className="tradingview-widget-container" ref={timelineWidgetRef}>
        <div className="tradingview-widget-copyright">
          <a
            href="https://www.tradingview.com/"
            rel="noopener nofollow"
            target="_blank"
          >
            <span className="blue-text">Track all markets on TradingView</span>
          </a>
        </div>
      </div>
    </nav>
  );
};

export default MarketChart;
