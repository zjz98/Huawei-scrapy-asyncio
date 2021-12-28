package columbus;

import java.util.List;

import graphlib.Attribute;
import graphlib.AttributeInt;
import graphlib.AttributeString;
import graphlib.Edge;
import graphlib.Edge.EdgeType;
import graphlib.Graph;
import graphlib.GraphlibException;
import graphlib.Node;
import graphlib.Attribute.aType;
import graphlib.VisitorException;
import graphsupportlib.Metric;

public class VisitorExample implements graphlib.Visitor {

  public static void main(String[] args) {

    if (args.length != 1) {
      System.out.println("Wrong number of arguments!");
      System.out.println("Usage: java -jar GraphExample.jar \"graph file\"");
      System.exit(1);
    }

    String graphFile = args[0];

    Graph graph = new Graph();
    try {
      graph.loadBinary(graphFile);

      Node root = graph.findNode(Metric.UID_LOGICAL_ROOT);

      Edge.EdgeTypeSet edgeTypeSet = new Edge.EdgeTypeSet();
      edgeTypeSet.add(new EdgeType(Metric.ETYPE_LIM_LOGICALTREE, Edge.eDirectionType.edtDirectional));

      graph.traverseDepthFirstPreorder(root, edgeTypeSet , new VisitorExample());

    } catch (GraphlibException | VisitorException e) {
      System.out.println("Error: cannot load binary graph: " + graphFile);
      System.exit(1);
    }
  }

  @Override
  public void edgeVisitorFunc(Edge arg0) throws VisitorException {
  }

  @Override
  public void postNodeVisitorFunc(Node arg0) throws VisitorException {
  }

  @Override
  public void preNodeVisitorFunc(Node node) throws VisitorException {
    if(node.getType().getType().equals(Metric.NTYPE_LIM_CLASS)) {
      String className = "";
      int LOC = 0;

      List<Attribute> attrs = node.findAttribute(aType.atString, Metric.ATTR_NAME, Metric.CONTEXT_ATTRIBUTE);
      if (attrs.size() == 1) {
        className = ((AttributeString) attrs.get(0)).getValue();
      }
      attrs = node.findAttribute(aType.atInt, "LOC", Metric.CONTEXT_METRIC);
      if (attrs.size() == 1) {
        LOC = ((AttributeInt) attrs.get(0)).getValue();
      }

      System.out.println("Class: " + className + " LOC: " + LOC);
    }
  }
}
