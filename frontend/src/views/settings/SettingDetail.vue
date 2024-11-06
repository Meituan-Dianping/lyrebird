<template>
    <div style="padding: 10px;">
        <v-list-item two-line style="padding-left: 25px;">
            <v-row>
                <v-col cols="9">
                    <v-list-item-content>
                        <v-list-item-title class="setting-name-title">
                            {{ settingsCurrentDetail.title }}
                        </v-list-item-title>
                        <v-list-item-subtitle style="margin-top: 5px;" class="setting-name-subtitle">{{
                            settingsCurrentDetail.notice }}</v-list-item-subtitle>
                    </v-list-item-content>
                </v-col>
                <v-col cols="3">
                    <v-btn depressed color="primary" class="settings-top-button" style="margin-top: 20px;" width="100" v-if="submitButtonText !== ''"
                        @click="submit">
                        {{ submitButtonText }}
                    </v-btn>
                    <v-tooltip bottom v-if="submitButtonText !== ''">
                    <template v-slot:activator="{ on, attrs }">
                        <v-btn
                        icon
                        large
                        class="settings-top-button"
                        @click="restore"
                        color="primary"
                        v-bind="attrs"
                        v-on="on"
                        >
                        <v-icon>mdi-cog-counterclockwise</v-icon>
                        </v-btn>
                    </template>
                    <span>{{ recoveryButtonText }}</span>
                    </v-tooltip>
                </v-col>
            </v-row>

        </v-list-item>
        <v-sheet height="80vh" class="overflow-y-auto" style="padding: 10px;">
            <v-list>
                <v-hover v-for="(config, index) in settingsCurrentDetail.configs" :key="index" v-slot="{ hover }">
                    <v-list-item three-line :class="{ 'bordered-hover': hover }">
                        <v-list-item-content class="setting-item-content">
                            <v-list-item-title class="setting-item-title">{{ config.title }}</v-list-item-title>
                            <v-list-item-subtitle class="setting-item-notice">{{ config.subtitle }}</v-list-item-subtitle>
                            <v-list-item-subtitle>
                                <!-- Bool Template -->
                                <v-switch v-if="config.category === 'bool'" v-model="submitForm[config.name]" hide-details dense
                                    class="setting-item-card setting-content-switch" inset></v-switch>

                                <!-- Text Template -->
                                <v-text-field v-if="config.category === 'text'" v-model="submitForm[config.name]"
                                    class="setting-item-card dense-font" hide-details single-line outlined dense>
                                </v-text-field>

                                <!-- Selector Template -->
                                <v-select v-else-if="config.category === 'selector'" v-model="submitForm[config.name]"
                                    class="setting-item-card dense-font" hide-details :items="config.options" outlined
                                    clearable dense>
                                </v-select>

                                <!-- Dict Template -->
                                <v-data-table v-else-if="config.category === 'dict'" dense :headers="dictHeaderTemplate"
                                    :items="submitForm[config.name]" item-key="index => index" hide-default-footer
                                    disable-sort disable-pagination disable-filtering>
                                    <template v-slot:item.k="item">
                                        <span v-if="item.item.isOp === false">{{ item.item.k }}</span>
                                        <v-text-field v-else class="data-table-dcit-text-field" v-model="item.item.k"
                                            hide-details single-line dense></v-text-field>
                                    </template>
                                    <template v-slot:item.v="item">
                                        <span v-if="item.item.isOp === false">{{ item.item.v }}</span>
                                        <v-text-field v-else class="data-table-dcit-text-field" v-model="item.item.v"
                                            hide-details single-line dense></v-text-field>
                                    </template>
                                    <template v-slot:item.opt="item">
                                        <v-btn icon color="#5f5cca" v-if="item.item.isOp === false"
                                            @click="removeTableItem(config.name, index)">
                                            <v-icon>mdi-delete</v-icon>
                                        </v-btn>
                                        <v-btn icon color="#5f5cca" v-else
                                            @click="addTableItem(config.name, config.category)">
                                            <v-icon>mdi-plus-circle-outline</v-icon>
                                        </v-btn>
                                    </template>
                                </v-data-table>

                                <!-- List Template -->
                                <v-data-table v-else-if="config.category === 'list'" dense :headers="listHeaderTemplate"
                                    :items="submitForm[config.name]" item-key="index => index" hide-default-footer
                                    disable-sort disable-pagination disable-filtering class="dense-font">
                                    <template v-slot:item.k="item">
                                        <span v-if="item.item.isOp === false">
                                            <v-icon>mdi-circle-small</v-icon>{{ item.item.k }}
                                        </span>
                                        <v-text-field v-else class="input-text-field" v-model="item.item.k" hide-details
                                            single-line dense></v-text-field>
                                    </template>
                                    <template v-slot:item.opt="item">
                                        <v-btn icon color="#5f5cca" v-if="item.item.isOp === false"
                                            @click="removeTableItem(config.name, index)">
                                            <v-icon>mdi-delete</v-icon>
                                        </v-btn>
                                        <v-btn icon color="#5f5cca" v-else
                                            @click="addTableItem(config.name, config.category)">
                                            <v-icon>mdi-plus-circle-outline</v-icon>
                                        </v-btn>
                                    </template>
                                </v-data-table>

                            </v-list-item-subtitle>
                        </v-list-item-content>
                    </v-list-item>
                </v-hover>
            </v-list>
        </v-sheet>
    </div>
</template>
  
<script>
import Vue from 'vue'
export default {
    data() {
        return {
            submitForm: {},
            submitButtonText: '',
            recoveryButtonText: 'Restore default',
            dictHeaderTemplate: [
                { textCn: '项', textEn: 'Key', value: 'k' },
                { textCn: '值', textEn: 'Value', value: 'v' },
                { textCn: '操作', textEn: 'Operate', value: 'opt' },
            ],
            listHeaderTemplate: [
                { textCn: '项', textEn: 'Key', value: 'k' },
                { textCn: '操作', textEn: 'Operate', value: 'opt' },
            ]
        }
    },
    components: {},
    computed: {
        settingsCurrentDetail() {
            return this.$store.state.settings.settingsCurrentDetail
        }
    },
    watch: {
        settingsCurrentDetail: {
            handler(newValue, oldValue) {
                // first load, no data
                this.$set(this, 'submitForm', {});
                if (typeof newValue.name === 'undefined') {
                    this.submitButtonText = ''
                    return
                }
                // change setting item, data refresh
                if (typeof newValue.submitText === 'string' && newValue.submitText.trim().length > 0) {
                    this.submitButtonText = newValue.submitText
                }
                if (newValue.language === 'cn') {
                    this.recoveryButtonText = '恢复默认'
                    for (const item of this.dictHeaderTemplate) {
                        item['text'] = item['textCn']
                    }
                    for (const item of this.listHeaderTemplate) {
                        item['text'] = item['textCn']
                    }
                } else {
                    this.recoveryButtonText = 'Restore default'
                    for (const item of this.dictHeaderTemplate) {
                        item['text'] = item['textEn']
                    }
                    for (const item of this.listHeaderTemplate) {
                        item['text'] = item['textEn']
                    }
                }

                for (const config of newValue.configs) {
                    if (config.category == 'text' || config.category == 'selector' || config.category == 'bool') {
                        this.submitForm[config.name] = config.data
                    } else if (config.category == 'dict') {
                        this.submitForm[config.name] = this.$set(this.submitForm, config.name, this.getDictItems(config.data))
                    } else if (config.category == 'list') {
                        this.submitForm[config.name] = this.$set(this.submitForm, config.name, this.getListItems(config.data))
                    }
                }
                console.log(this.submitForm)
            },
            immediate: true
        },
    },
    methods: {
        getDictItems(dict) {
            let items = Object.entries(dict).map(([k, v]) => ({ k, v, isOp: false }))
            items.push({ k: '', v: '', isOp: true })
            return items
        },
        getListItems(list) {
            return [...list.map(item => ({ k: item, isOp: false })), { k: '', isOp: true }];
        },
        removeTableItem(name, index) {
            this.submitForm[name].splice(index, 1);
        },
        removeDictItem(dict, key) {
            this.$delete(dict, key);
        },
        removeListItem(list, item) {
            const index = list.indexOf(item);
            if (index > -1) {
                list.splice(index, 1);
            }
        },
        convertDictToOri(data) {
            const resp = {};
            data.forEach(item => {
                if (!item.isOp && item.k && item.v) {
                    resp[item.k] = item.v;
                }
            });
            return resp;
        },
        convertListToOri(data) {
            const resp = [];
            data.forEach(item => {
                if (!item.isOp && item.k) {
                    resp.push(item.k)
                }
            });
            return resp;
        },
        addTableItem(name, category) {
            let tableData = this.submitForm[name]
            if (category == 'dict') {
                tableData[tableData.length - 1]['isOp'] = false
                tableData.push({ k: '', v: '', isOp: true })
            } else if (category == 'list') {
                tableData[tableData.length - 1]['isOp'] = false
                tableData.push({ k: '', isOp: true })
            }
        },
        submit() {
            let data = {}
            for (const config of this.settingsCurrentDetail.configs) {
                if (config.category == 'text' || config.category == 'selector' || config.category == 'bool') {
                    data[config.name] = this.submitForm[config.name]
                } else if (config.category == 'dict') {
                    data[config.name] = this.convertDictToOri(this.submitForm[config.name])
                } else if (config.category == 'list') {
                    data[config.name] = this.convertListToOri(this.submitForm[config.name])
                }

            }
            this.$store.dispatch('saveSettingsForm', {
                'formName': this.settingsCurrentDetail.name,
                'formData': data
            })
        },
        restore() {
            this.$store.dispatch('restoreSettingsForm', this.settingsCurrentDetail.name)
        }
    },
    mounted() {

    },
}
</script>
  
<style scoped>
.setting-name-title {
    font-weight: 600;
    font-size: 18px;
    color: #5f5cca !important;
}

.setting-name-subtitle {
    font-weight: 400;
    font-size: 12px;
    color: #9B9CB7 !important;
}

.setting-item-title {
    font-family: PingFangSC-Regular;
    color: #000520 !important;
    font-weight: 400;
    font-size: 14px;
    margin-bottom: 5px;
}

.setting-item-notice {
    font-family: PingFangSC-Regular;
    color: #9B9CB7 !important;
    font-weight: 400;
    font-size: 12px;
    margin-bottom: 5px;
}

.setting-item-card {
    padding: 0px;
    max-width: 500px;
    max-height: 500px;
    margin-top: 5px;
}

.setting-item-content {
    padding-top: 15px;
    padding-bottom: 15px;
}

.setting-content-switch {
    margin-left: 5px;
}

.data-table-list-text-field {
    max-width: 90%;
    padding-left: 24px;
}

.data-table-dcit-text-field {
    max-width: 90%;
}

.v-list-item {
    border: 1px solid transparent;
    box-sizing: border-box;
    transition: border-color 0.3s ease;
}

.bordered-hover {
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
}

.dense-font {
    font-size: 14px;
}

.settings-top-button {
    margin-top: 20px;
    margin-left: 2px;
}

::v-deep .v-text-field__slot input {
    padding-top: 4px;
    padding-bottom: 4px;
}

::v-deep .v-select__selections input {
    padding-top: 0px;
    padding-bottom: 0px;
}

::v-deep .v-select.v-input--dense .v-select__selection--comma {
    margin-top: 0;
    margin-bottom: 0;
}

::v-deep .v-text-field--enclosed.v-input--dense:not(.v-text-field--solo).v-text-field--outlined .v-input__append-inner {
    margin-top: 4px;
}

::v-deep .v-select__selections {
    padding-top: 4px;
    padding-bottom: 4px;
}

::v-deep .setting-item-card.v-text-field--outlined.v-input--dense>.v-input__control>.v-input__slot {
    min-height: 30px;
}

::v-deep .no-hover-shadow .v-input--selection-controls__ripple {
  box-shadow: none !important;
}

::v-deep .no-hover-shadow .v-input--selection-controls__ripple:hover {
  box-shadow: none !important;
}

</style>
  