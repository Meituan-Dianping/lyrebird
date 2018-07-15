module.exports = {
    locales: {
        '/': {
            base: 'lyrebird',
            lang: 'zh-CN',
            title: 'Lyrebird',
            description: '客户端测试工作台'
        }
    },
    themeConfig: {
        nav: [
            { text: '首页', link: '/' },
            { text: '使用指南', link: '/guide/' },
            { text: '开发者指南', link: '/develop/' },
            {
                text: 'RELEASE', link: '/releases/'
            },
            {
                text: '代码仓库',
                items: [
                    { text: 'Lyrebird', link: 'https://github.com/meituan/lyrebird' },
                    { text: 'iOS', link: 'https://github.com/meituan/lyrebird-ios' },
                    { text: 'Android', link: 'https://github.com/meituan/lyrebird-android' },
                    { text: 'ApiCoverage', link: 'https://github.com/meituan/lyrebird-api-coverage' }
                ]
            }
        ],
        sidebar: {
            '/guide/': [
                'quickstart',
                '',
                'faq'
            ],
            '/develop/': [
                ''
            ],
            '/releases/': [
                '',
                'history'
            ],
            '/aboutus/': [
                ''
            ]
        }
    }
}