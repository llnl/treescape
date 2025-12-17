ST.FlameGraphModel = function () {

    var nodes_idx_by_name_;
    var width_scaler_ = 1;
    var color_map_ = {};

    //  This creates the tree content but puts it in a obj referenced format
    var index_nodes_by_name_ = function (nodes_item, agg, index_to_get) {

        var nos = {};
        var perftree = nodes_item[ index_to_get ].perftree;

        for (var i in perftree) {
            nos[i] = perftree[i][agg];
        }

        return nos;
    };


    function createTree(obj, key, level, agg) {

        //var mag = 80 / (Math.pow(2, level));
        var first_ydata = nodes_idx_by_name_[key];

        var mag = parseInt(first_ydata * width_scaler_);
        mag = mag < 0 ? 0 : mag;

        const node = {name: key, level, magnitude: mag};
        const children = obj[key];

        if (children && children.length > 0) {
            node.children = children.map(childKey => createTree(obj, childKey, level + 1, agg));
            node.magnitude = mag;
        }

        node.color = getSpot2Color_(node.name, node.children);
        color_map_[node.name] = node.color;

        return node;
    }


    function getSpot2Color_(name, children) {

        var suffix = "";

        if (children) {
            for (var i = 0; i < children.length; i++) {

                if (children[i]) {
                    suffix += children[i].name;
                }
            }
        }

        //var colorH = hashStringToNumber(name + suffix);
        var colorH = spot2ColorHash(name + suffix);

        // Generate random values for red, green, and blue components
        // Combine components into a CSS color string
        return colorH;
    };

    function spot2ColorHash(text, alpha) {
        const reverseString = text.split("").reverse().join("")
        const hash = jQuery.md5(reverseString)
        const r = parseInt(hash.slice(12, 14), 16)
        const g = parseInt(hash.slice(14, 16), 16)
        const b = parseInt(hash.slice(16, 18), 16)
        return `rgb(${r}, ${g}, ${b}, 0.6)`
    }


    var get_ = function (ef, index_to_get, agg) {

        nodes_idx_by_name_ = index_nodes_by_name_(ef.nodes, agg, index_to_get);

        // Use per-run childrenMap if available, otherwise fall back to global
        var cm = ef.childrenMap;  // Default to global childrenMap

        if (ef.nodes && ef.nodes[index_to_get] && ef.nodes[index_to_get].childrenMap) {
            // Use the specific run's childrenMap
            cm = ef.nodes[index_to_get].childrenMap;
        } else if( !ef.childrenMap ) {
            console.log('************** Warning: I do not have a childrenMap. ********************');
        }

        const root = Object.keys(cm)[0];
        var topWidth = 620;

        if( nodes_idx_by_name_[root] ) {
            topWidth = nodes_idx_by_name_[root];
        }

        var flameContainerWidth = $('.flameContainer').width();

        var calc_width_scale = flameContainerWidth / topWidth;
        width_scaler_ = calc_width_scale;

        //  debug code.
        var tmp_first_ydata = nodes_idx_by_name_[root];

        const tree0 = createTree(cm, root, 0, agg);

        return {
            tree: tree0,
            max: nodes_idx_by_name_['main']
        }
    };


    var get_color_by_name_ = function( node_name ) {
        return color_map_[node_name] || "#eeeeee";
    };


    return {
        get_color_by_name: get_color_by_name_,
        get: get_
    }
}();
