<template>
    <tr>
        <td>
            <input type="checkbox" :id="flow.id" v-model="selected">
        </td>
        <td>
            <span class="label" :class="[responseSrcClass]">{{responseSrc}}</span>
        </td>
        <td>
            <strong>
                <span :class="[codeClass]">{{flow.response.code}}</span>
            </strong>
        </td>
        <td>
            {{flowContent.hostname}}
        </td>
        <td>
            {{flowContent.pathname}}
        </td>
    </tr>
</template>