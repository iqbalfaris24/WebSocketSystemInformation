/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable no-unused-vars */
import { useState, useEffect, useRef } from "react";
import { Chart as ChartJS, ArcElement, Legend } from "chart.js";
import { Doughnut } from "react-chartjs-2";
import { Switch } from "@/components/ui/switch";
import { io } from "socket.io-client";
import { FiSun, FiMoon, FiEye } from "react-icons/fi";
import { disconnect } from "process";

ChartJS.register(ArcElement, Legend);

function App() {
  const [connected, setConnected] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [status, setStatus] = useState({
    cpu: {
      current: 0,
      min: 0,
      max: 0,
      temperature: 0,
    },
    memory_percent: 0,
    memory_total: 0,
    memory_used: 0,
    storage_percent: 0,
    storage_total: 0,
    storage_used: 0,
  });
  const socket = io("https://systemstatus.iqbalfaris.my.id", {
    autoConnect: false,
    transports: ["websocket"], // Prioritaskan WebSocket
  });
  const socketRef = useRef(socket);

  useEffect(() => {
    socketRef.current.connect();

    socketRef.current.on("connect", () => {
      setConnected(true);
    });

    socketRef.current.on("disconnect", () => {
      setConnected(false);
    });

    socketRef.current.on("status_update", (data) => {
      setStatus(data);
    });

    return () => {
      socketRef.current.off("connect");
      socketRef.current.off("disconnect");
      socketRef.current.off("status_update");
    };
  }, [socketRef]);

  const cpuData = {
    datasets: [
      {
        data: [
          (status.cpu.current / 2.0) * 100,
          100 - (status.cpu.current / 2.0) * 100,
        ],
        backgroundColor: ["#4caf50", "#e0e0e0"],
        borderWidth: 0,
      },
    ],
  };

  const memoryData = {
    datasets: [
      {
        data: [status.memory_percent, 100 - status.memory_percent],
        backgroundColor: ["#42a5f5", "#e0e0e0"],
        borderWidth: 0,
      },
    ],
  };

  const storageData = {
    datasets: [
      {
        data: [status.storage_percent, 100 - status.storage_percent],
        backgroundColor: ["#ff7043", "#e0e0e0"],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    cutout: "85%",
    responsive: true,
    plugins: {
      // tooltip: { enabled: false },
      // legend: { display: false },
    },
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem("darkMode", JSON.stringify(newMode)); // Simpan ke local storage
  };

  useEffect(() => {
    const savedDarkMode = JSON.parse(
      localStorage.getItem("darkMode") || "false"
    );
    setDarkMode(savedDarkMode);
  }, []);

  return (
    <div className={`${darkMode ? "dark" : ``}`}>
      {/* Navbar */}
      <div className="navbar flex bg-dark-blue text-white justify-center py-4">
        <div className="flex justify-between container">
          <a className="btn btn-ghost text-xl hidden md:block">Dashboard</a>
          <div className="right-option flex gap-4 items-center w-full justify-around md:justify-end ">
            <div className="flex items-center gap-1">
              <FiSun color={`${darkMode ? "#ffffff" : "#FFDE59"}`} />
              <Switch checked={darkMode} onCheckedChange={toggleDarkMode} />
              <FiMoon color={`${darkMode ? "#000000" : "#ffffff"}`} />
            </div>
            <div className="status flex bg-navy-blue text-white p-2 rounded-md items-center gap-2">
              <h6>
                Status:{" "}
                <span
                  className={`${connected ? `text-green-500` : `text-red-500`}`}
                >
                  {connected ? "Connected" : "Disconnected"}
                </span>
              </h6>
              <span className="relative flex h-3 w-3">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    connected ? `bg-green-400` : `bg-red-400`
                  }`}
                ></span>
                <span
                  className={`relative inline-flex rounded-full h-3 w-3 ${
                    connected ? `bg-green-500` : `bg-red-500`
                  }`}
                ></span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Page */}
      <div className="flex justify-center bg-white min-h-screen dark:bg-navy-blue dark:text-white">
        <div className="container mt-4 md:mt-12">
          {/* system status */}
          <div className="grid grid-cols-1 md:grid-cols-1 gap-4 mx-2 md:mx-0 xl:grid-cols-3">
            <div className="card flex flex-wrap justify-center min-h-40 p-4 rounded-sm text-white bg-dark-blue md:flex-nowrap md:rounded-3xl">
              <div className="chart relative w-32 h-32 -mt-1">
                <Doughnut data={cpuData} options={options} />
                <div
                  className=""
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    fontSize: "24px",
                    fontWeight: "bold",
                  }}
                >
                  {((status.cpu.current / 2.0) * 100).toFixed(1)}%
                </div>
              </div>
              <div className="descripion w-full flex justify-center flex-wrap">
                <h1 className="text-center font-bold text-3xl	">CPU Status</h1>
                <table className="table-fixed w-9/12">
                  <tbody>
                    <tr>
                      <td className="text-start">Current Speed</td>
                      <td className="w-1/3">: {status.cpu.current} Ghz</td>
                    </tr>
                    <tr>
                      <td className="text-start">Current Temperature</td>
                      <td className="w-1/3">: {status.cpu.temperature}°</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card flex flex-wrap justify-center min-h-40 p-4 rounded-sm text-white bg-dark-blue md:flex-nowrap md:rounded-3xl">
              <div className="chart relative w-32 h-32 -mt-1">
                <Doughnut data={memoryData} options={options} />
                <div
                  className=""
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    fontSize: "24px",
                    fontWeight: "bold",
                  }}
                >
                  {status.memory_percent}%
                </div>
              </div>
              <div className="descripion w-full flex justify-center flex-wrap">
                <h1 className="text-center font-bold text-3xl	">
                  Memory Status
                </h1>
                <table className="table-fixed w-9/12">
                  <tbody>
                    <tr>
                      <td className="text-start">Used Memory</td>
                      <td className="w-1/3">: {status.memory_used} GB</td>
                    </tr>
                    <tr>
                      <td className="text-start">Total Memory</td>
                      <td className="w-1/3">: {status.memory_total} GB</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card flex flex-wrap justify-center min-h-40 p-4 rounded-sm text-white bg-dark-blue md:flex-nowrap md:rounded-3xl">
              <div className="chart relative w-32 h-32 -mt-1">
                <Doughnut data={storageData} options={options} />
                <div
                  className=""
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    fontSize: "24px",
                    fontWeight: "bold",
                  }}
                >
                  {status.storage_percent}%
                </div>
              </div>
              <div className="descripion w-full flex justify-center flex-wrap">
                <h1 className="text-center font-bold text-3xl	">
                  Storage Status
                </h1>
                <table className="table-fixed w-9/12">
                  <tbody>
                    <tr>
                      <td className="text-start">Used Storage</td>
                      <td className="w-1/3">: {status.storage_used} GB</td>
                    </tr>
                    <tr>
                      <td className="text-start">Total Storage</td>
                      <td className="w-1/3">: {status.storage_total} GB</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* domain status */}
          <div className="mt-8 mx-2 overflow-x-auto">
            <table className="w-full lg:w-1/2 border-b-2">
              <thead className="">
                <tr className="border-y-2">
                  <th className="py-2 w-44">Domain</th>
                  <th className="w-14">Status</th>
                  <th className="w-14">View</th>
                </tr>
              </thead>
              <tbody>
                <tr className="text-center">
                  <td className="py-1">
                    <a
                      href="http://iqbalfaris.my.id"
                      className=" hover:text-blue-400"
                      target="blank"
                    >
                      iqbalfaris.my.id
                    </a>
                  </td>
                  <td className="text-green-500">Active</td>
                  <td className="">
                    <label
                      htmlFor=""
                      className="flex items-center justify-center"
                    >
                      <FiEye />
                      &nbsp;{status.log_status?.portfolio}
                    </label>
                  </td>
                </tr>
                <tr className="text-center">
                  <td className="py-1 ">
                    <a
                      href="http://ipcreative.iqbalfaris.my.id"
                      className=" hover:text-blue-400"
                      target="blank"
                    >
                      ipcreative.iqbalfaris.my.id
                    </a>
                  </td>
                  <td className="text-green-500">Active</td>
                  <td className="">
                    <label
                      htmlFor=""
                      className="flex items-center justify-center"
                    >
                      <FiEye />
                      &nbsp;{status.log_status?.ipcreative}
                    </label>
                  </td>
                </tr>
                <tr className="text-center">
                  <td className="py-1">
                    <a
                      href="http://pemilihansupplier.iqbalfaris.my.id"
                      className=" hover:text-blue-400"
                      target="blank"
                    >
                      pemilihansupplier.iqbalfaris.my.id
                    </a>
                  </td>
                  <td className="text-green-500">Active</td>
                  <td className="">
                    <label
                      htmlFor=""
                      className="flex items-center justify-center"
                    >
                      <FiEye />
                      &nbsp;{status.log_status?.pemilihanSupplier}
                    </label>
                  </td>
                </tr>
                <tr className="text-center">
                  <td className="py-1">
                    <a
                      href="http://dashboardsystem.iqbalfaris.my.id"
                      className=" hover:text-blue-400"
                      target="blank"
                    >
                      dashboardsystem.iqbalfaris.my.id
                    </a>
                  </td>
                  <td className="text-green-500">Active</td>
                  <td className="">
                    <label
                      htmlFor=""
                      className="flex items-center justify-center"
                    >
                      <FiEye />
                      &nbsp;{status.log_status?.dashboardSystem}
                    </label>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
