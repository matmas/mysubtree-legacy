// node
//     inside
//         voting
//         title
//         body
//         permalink
//         branching
//             paste
//     typeContainer
//         addContainer
//         nodelist
//             nodes
//                 node
//                     inside
//                         voting
//                             voteIndicator
//                         title
//                         body
//                         user
//                         permalink
//                         branching
//                             paste
//                     typeContainer
//                         addContainer
//                         nodelist
// -----------------------------------------------------------
var Voting = function(elem) {
    this.$ = $(elem).closest('td.voting');
}
// -----------------------------------------------------------
var Title = function(elem) {
    this.$ = $(elem).closest('span.title');
}
// -----------------------------------------------------------
var Body = function(elem) {
    this.$ = $(elem).closest('span.body');
}
// -----------------------------------------------------------
var Permalink = function(elem) {
    this.$ = $(elem).closest('a.permalink');
}
// -----------------------------------------------------------
var Paste = function(elem) {
    this.$ = $(elem).closest('span.paste');
}
// -----------------------------------------------------------
var Branching = function(elem) {
    this.$ = $(elem).closest('div.branching');
}
// -----------------------------------------------------------
Branching.prototype.paste = function() {
    return new Paste(this.$.children('span.paste').get(0));
}
// -----------------------------------------------------------
var Inside = function(elem) {
    this.$ = $(elem).closest('tr.inside');
}
// -----------------------------------------------------------
Inside.prototype.voting = function() {
    return new Voting(this.$.children('td.voting').get(0));
}
// -----------------------------------------------------------
Inside.prototype.title = function() {
    return new Title(this.$.children('td.td-n').children('div.inside-inside').children('div.node-top').children('span.title').get(0));
}
// -----------------------------------------------------------
Inside.prototype.body = function() {
    return new Body(this.$.children('td.td-n').children('div.inside-inside').children('div.node-top').children('span.body').get(0));
}
// -----------------------------------------------------------
Inside.prototype.permalink = function() {
    return new Permalink(this.$.children('td.td-n').children('div.inside-inside').children('div.node-top').children('span.node-info').children('a.permalink').get(0));
}
// -----------------------------------------------------------
Inside.prototype.branching = function() {
    return new Branching(this.$.children('td.td-n').children('div.inside-inside').children('div.branching').get(0));
}
// -----------------------------------------------------------
var AddContainer = function(elem) {
    this.$ = $(elem).closest('div.add-container');
}
// -----------------------------------------------------------
var VoteIndicator = function(elem) {
    this.$ = $(elem).closest('span.vote-indicator');
}
// -----------------------------------------------------------
Voting.prototype.voteIndicator = function() {
    return new VoteIndicator(this.$.children('span.vote-indicator').get(0));
}
// -----------------------------------------------------------
var User = function(elem) {
    this.$ = $(elem).closest('a.user');
}
// -----------------------------------------------------------
Inside.prototype.user = function() {
    return new User(this.$.children('td.td-n').children('div.inside-inside').children('div.node-top').children('span.node-info').children('a.user').get(0));
}
// -----------------------------------------------------------
var Nodelist = function(elem) {
    this.$ = $(elem).closest('div.nodelist');
}
// -----------------------------------------------------------
var TypeContainer = function(elem) {
    this.$ = $(elem).closest('td.type-container');
}
// -----------------------------------------------------------
TypeContainer.prototype.addContainer = function() {
    if (this.$.children('div.add-container').length == 0) {
        var elem = this.$;
        elem = $("<div class='add-container'></div>").prependTo(elem);
    }
    return new AddContainer(this.$.children('div.add-container').get(0));
}
// -----------------------------------------------------------
TypeContainer.prototype.nodelist = function() {
    return new Nodelist(this.$.children('div.nodelist').get(0));
}
// -----------------------------------------------------------
var Node = function(elem) {
    this.$ = $(elem).closest('tbody.node');
}
// -----------------------------------------------------------
Node.prototype.inside = function() {
    return new Inside(this.$.children('tr.inside').get(0));
}
// -----------------------------------------------------------
Node.prototype.typeContainer = function() {
    return new TypeContainer(this.$.children('tr.tr-c').children('td.type-container').get(0));
}
// -----------------------------------------------------------
var Nodes = function(elem) {
    this.$ = $(elem).closest('table.nodes');
}
// -----------------------------------------------------------
Nodes.prototype.node = function() {
    return new Node(this.$.children('tbody.node').get(0));
}
// -----------------------------------------------------------
Nodelist.prototype.nodes = function() {
    return new Nodes(this.$.children('div.node-list').children('table.nodes').get(0));
}
// -----------------------------------------------------------
// user
// -----------------------------------------------------------
// nodes
//     node
//         inside
//             voting
//                 voteIndicator
//             title
//             body
//             user
//             permalink
//             branching
//                 paste
//         typeContainer
//             addContainer
//             nodelist
// -----------------------------------------------------------
// node
//     inside
//         voting
//         title
//         body
//         permalink
//         branching
//             paste
//     typeContainer
//         addContainer
//         nodelist
//             nodes
//                 node
//                     inside
//                         voting
//                             voteIndicator
//                         title
//                         body
//                         user
//                         permalink
//                         branching
//                             paste
//                     typeContainer
//                         addContainer
//                         nodelist
//                             nodes
//                                 node
//                                     inside
//                                         voting
//                                             voteIndicator
//                                         title
//                                         body
//                                         user
//                                         permalink
//                                         branching
//                                             paste
//                                     typeContainer
//                                         addContainer
//                                         nodelist
