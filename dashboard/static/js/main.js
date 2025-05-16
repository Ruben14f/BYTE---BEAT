document.getElementById("filtro-fechas").addEventListener("submit", async (event) => {
    event.preventDefault();

    const desde = document.getElementById("desde").value;
    const hasta = document.getElementById("hasta").value;

    const chartDom = document.getElementById("chart");
    const chartDom2 = document.getElementById("chart2");

    const myChart = echarts.init(chartDom);
    const myChart2 = echarts.init(chartDom2);

    const params = new URLSearchParams();
    if (desde) params.append("desde", desde);
    if (hasta) params.append("hasta", hasta);

    const url = `http://127.0.0.1:8000/admin-dashboard/api/get-chart/?${params.toString()}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.resetFiltros) {
            document.getElementById("desde").value = "";
            document.getElementById("hasta").value = "";
            alert("No se encontraron órdenes en la fecha seleccionada. Mostrando todos los datos.");
        }

        myChart.setOption(data);
        myChart.resize();

        myChart2.setOption(data);
        myChart2.resize();
    } catch (error) {
        console.error("Error fetching filtered chart data:", error);
    }
});
