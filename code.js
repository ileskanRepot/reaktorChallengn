const droneTable = document.getElementById("drones")

const main = async () => {
	const drones = await fetch("/reaktor/drones.py")
	.then(res => res.json())

	droneTable.innerHTML = ""

	const row = document.createElement("tr")

	Object.keys(drones[0]).forEach(item => {
		const slot = document.createElement("th")
		slot.appendChild(document.createTextNode(item))
		row.appendChild(slot)
	})

	droneTable.appendChild(row)

	drones.forEach(drone => {
		const row = document.createElement("tr")
		Object.keys(drone).forEach(item => {
			const slot = document.createElement("td")
			slot.appendChild(document.createTextNode(drone[item]))
			row.appendChild(slot)
		})
		droneTable.appendChild(row)
	})
	const loading = document.getElementById("loading")
	if (loading) loading.remove()
}

main()
setInterval(main,10000)
