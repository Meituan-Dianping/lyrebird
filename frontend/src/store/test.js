export const data_mapping = [
    {
      name: 'Business A',
      id: '001',
      type: 'group',
      children: [
        {
          name: 'v1.0.3',
          id: '002',
          type: 'group',
          children: [
            {
              name: 'homepage/detail',
              id: '003',
              type: 'data'
            },
            {
              name: 'homepage/advertise',
              id: '004',
              type: 'data'
            },
            {
              name: 'poi/detail',
              id: '005',
              type: 'data'
            }
          ]
        },
        {
          name: 'v1.0.6',
          id: '006',
          type: 'group',
          children: [
            {
              name: 'homepage/detail',
              id: '003',
              type: 'data'
            },
            {
              name: 'homepage/advertise',
              id: '004',
              type: 'data'
            },
            {
              name: 'poi/detail',
              id: '005',
              type: 'data'
            }
          ]
        }
      ]
    },
    {
      name: 'Business B',
      id: '010',
      type: 'group',
      children: [
        {
          name: 'http://www.google.com',
          id: '011',
          children: [
            {
              name: 'ususl',
              id: '012',
              type: 'data'
            },
            {
              name: 'error',
              id: '013',
              type: 'data'
            },
            {
              name: 'empty',
              id: '014',
              type: 'data'
            }
          ]
        },
        {
          name: 'https://www.baidu.com',
          id: '015',
          type: 'group',
          children: [
            {
              name: 'ususl',
              id: '012',
              type: 'data'
            },
            {
              name: 'error',
              id: '013',
              type: 'data'
            },
            {
              name: 'empty',
              id: '014',
              type: 'data'
            }
          ]
        },
        {
          name: 'https://www.meituan.com',
          id: '019',
          type: 'group',
          children: [
            {
              name: 'ususl',
              id: '012',
              type: 'data'
            },
            {
              name: 'error',
              id: '013',
              type: 'data'
            },
            {
              name: 'empty',
              id: '014',
              type: 'data'
            }
          ]
        }
      ]
    }
  ]