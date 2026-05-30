import { Node, nodeInputRule } from '@tiptap/core'

/**
 * 自定义 inline atomic Node：**数字** → #数字 超链接
 * 输入 **524** → 渲染为蓝色 #524，点击跳转卦例详情
 * atom=true 使得删除时整体删除（按退格整块删掉）
 */
export default Node.create({
  name: 'guaLink',

  group: 'inline',
  inline: true,
  atom: true,

  addAttributes() {
    return {
      id: { default: null },
    }
  },

  parseHTML() {
    return [{
      tag: 'span.gua-link',
      getAttrs: node => ({ id: node.getAttribute('data-id') }),
    }]
  },

  renderHTML({ node }) {
    return [
      'span',
      { class: 'gua-link', 'data-id': node.attrs.id },
      `#${node.attrs.id}`,
    ]
  },

  addInputRules() {
    return [
      nodeInputRule({
        find: /(\*\*(\d+)\*\*)$/,
        type: this.type,
        getAttributes: match => ({ id: match[2] }),
      }),
    ]
  },
})
