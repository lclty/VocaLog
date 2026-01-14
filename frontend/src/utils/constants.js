// 定义基础工种顺序
export const STAFF_ROLES = [
    '策划', 
    '作曲', 
    '编曲', 
    '演奏', 
    '作词', 
    '调教', // 这是一个排序锚点，实际工种是 "调教 (洛天依...)"
    '混音', 
    '曲绘', 
    'PV制作', 
    '剪辑', 
    '封面设计',
    '题字', 
    '演唱'
];

// 提供一个辅助排序函数，供各组件使用
export const sortRoles = (roles) => {
    return roles.sort((a, b) => {
        // 获取基础工种名（处理 "调教 (...)" 这种情况）
        const getBaseRole = (r) => {
            if (r.startsWith('调教')) return '调教';
            if (r === 'PV') return 'PV制作'; // 兼容
            return r;
        };

        const indexA = STAFF_ROLES.indexOf(getBaseRole(a));
        const indexB = STAFF_ROLES.indexOf(getBaseRole(b));

        // 如果都在列表里，按列表顺序
        if (indexA !== -1 && indexB !== -1) {
            // 如果都是调教，则按字母序细分
            if (indexA === indexB) return a.localeCompare(b);
            return indexA - indexB;
        }
        
        // 如果有一个不在列表里（比如自定义的新工种），放到最后
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
        return 0;
    });
};