const alfy = require('alfy')

const gifz = 'https://gifz.netlify.app/'
const data = await alfy.fetch(`${gifz}gifs.json`)

const items = alfy
	.inputMatches(data, 'keywords')
	.map(element => ({
		title: element.keywords,
    arg: gifz + element.url
	}))

alfy.output(items)
